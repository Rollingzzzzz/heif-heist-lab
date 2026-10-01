#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_gif.py — HEIF Heist akış GIF'i üretici.
README için animasyonlu diyagram: yükleme sayfası → dosya baytları →
libheif'teki taşma → heap sızıntısı → avatar → ASAN kanıtı.

Kullanım: python docs/gif/make_gif.py
Çıktı:    docs/screenshots/heif-heist-flow.gif
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- sabitler
W, H = 880, 560
BG      = "#0d1117"
PANEL   = "#161b22"
BORDER  = "#30363d"
TEXT    = "#e6edf3"
DIM     = "#8b949e"
GREEN   = "#3fb950"
CYAN    = "#58a6ff"
RED     = "#f85149"
YELLOW  = "#d29922"
PURPLE  = "#bc8cff"
ORANGE  = "#f0883e"
FBBLUE  = "#1877f2"

FONT_DIR = "C:/Windows/Fonts"
_F_CACHE = {}


def _truetype(size: int, bold: bool):
    key = (size, bold)
    if key not in _F_CACHE:
        name = "consolab.ttf" if bold else "consola.ttf"
        _F_CACHE[key] = ImageFont.truetype(f"{FONT_DIR}/{name}", size)
    return _F_CACHE[key]


random.seed(115000)


def font(size, bold=False):
    return _truetype(size, bold)


def new_frame():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def header(d, step, total, title, color=CYAN):
    """Üst başlık şeridi: adım sayacı + başlık."""
    d.rectangle([0, 0, W, 54], fill=PANEL)
    d.line([0, 54, W, 54], fill=BORDER, width=1)
    d.text((20, 16), title, font=font(20, bold=True), fill=color)
    # adım pilleri
    x = W - 20
    for i in range(total - 1, -1, -1):
        c = color if i <= step else BORDER
        d.ellipse([x - 14, 20, x, 34], fill=c)
        x -= 20
    d.text((20, 34), "heif-heist-lab", font=font(13), fill=DIM)


def panel(d, box, title=None, border=BORDER):
    d.rounded_rectangle(box, radius=8, fill=PANEL, outline=border, width=1)
    if title:
        d.text((box[0] + 14, box[1] + 10), title, font=font(15, bold=True), fill=DIM)


# ------------------------------------------------------- sahne 1: yükleme
def scene_upload(progress: float):
    """feysbuk yükleme sayfası + HEIC dosyası butona doğru uçuyor."""
    img, d = new_frame()
    header(d, 0, 5, "1 — Sıradan kullanıcı, profil fotoğrafı yüklüyor", CYAN)

    # tarayıcı mockup
    bx0, by0, bx1, by1 = 90, 90, 790, 500
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=10, fill="#0d1117", outline=BORDER)
    d.rectangle([bx0, by0 + 34, bx1, by0 + 60], fill=PANEL)
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        d.ellipse([bx0 + 14 + i * 22, by0 + 12, bx0 + 26 + i * 22, by0 + 24], fill=c)
    d.rounded_rectangle([bx0 + 90, by0 + 10, bx1 - 16, by0 + 28], radius=12, fill="#0d1117", outline=BORDER)
    d.text((bx0 + 104, by0 + 12), "http://feysbuk.test/home.php", font=font(13), fill=DIM)

    # feysbuk üst bar
    d.rectangle([bx0, by0 + 60, bx1, by0 + 100], fill=FBBLUE)
    d.text((bx0 + 20, by0 + 68), "feysbuk", font=font(24, bold=True), fill="#ffffff")

    # yükleme kartı
    card = [bx0 + 180, by0 + 130, bx1 - 180, by0 + 330]
    d.rounded_rectangle(card, radius=10, fill=PANEL, outline=BORDER)
    d.text((card[0] + 20, card[1] + 14), "Profil Fotoğrafı (HEIC)", font=font(17, bold=True), fill=TEXT)

    # dosya seçici
    fs = [card[0] + 20, card[1] + 56, card[0] + 320, card[1] + 92]
    d.rectangle(fs, fill="#0d1117", outline=BORDER)
    d.rectangle([fs[0], fs[1], fs[0] + 96, fs[1] + 36], fill="#21262d", outline=BORDER)
    d.text((fs[0] + 10, fs[1] + 9), "Choose File", font=font(13), fill=TEXT)
    d.text((fs[0] + 108, fs[1] + 9), "gunun-karesi.heic", font=font(13), fill=GREEN)

    # buton (progress ile parlıyor)
    btn = [card[0] + 20, card[1] + 130, card[0] + 260, card[1] + 172]
    glow = 0.5 + 0.5 * progress
    bcol = FBBLUE if glow < 0.9 else "#4a90ff"
    d.rounded_rectangle(btn, radius=8, fill=bcol)
    d.text((btn[0] + 34, btn[1] + 12), "Yükle ve Dönüştür", font=font(15, bold=True), fill="#ffffff")
    d.text((card[0] + 20, card[1] + 190),
           "Yüklediğin dosya sunucuda heifconv (libheif 1.17.6) ile işlenir.",
           font=font(13), fill=DIM)

    # uçan dosya ikonu
    fx = card[0] + 140 - 260 * progress
    fy = card[1] - 60 + (130 + 40) * progress
    if progress > 0.02:
        d.rounded_rectangle([fx - 26, fy - 16, fx + 26, fy + 16], radius=4,
                            fill="#21262d", outline=GREEN, width=2)
        d.text((fx - 20, fy - 8), ".heic", font=font(13, bold=True), fill=GREEN)

    d.text((20, H - 34), "Dosya masum görünüyor… ama içinde bir YALAN var  →",
           font=font(15), fill=YELLOW)
    return img


# ------------------------------------------------- sahne 2: dosya anatomisi
HEX_LINES = [
    ("00000000", "00 00 00 20 66 74 79 70", "ftyp mif1", DIM),
    ("00000020", "00 00 00 f9 6d 65 74 61", "meta hdlr", DIM),
    ("00000090", "00 00 00 60 00 00 00 60", "ispe w=96 h=96", GREEN),
    ("000000a0", "75 6e 63 43 00 00 00 00", "uncC planar", GREEN),
    ("00000140", "69 6c 6f 63 65 78 74 3d", "iloc extent=96", YELLOW),
    ("00000160", "48 45 49 53 54 2d 53 45", "HEIST-SE..", RED),
]


def scene_bytes(reveal: float):
    img, d = new_frame()
    header(d, 1, 5, "2 — Dosyanın anatomisi: bir YALAN", YELLOW)

    panel(d, [60, 80, 460, 420], "crash.heic — hexdump (385 bayt)")
    n = max(1, int(len(HEX_LINES) * min(1.0, reveal * 1.4)))
    y = 120
    for off, hexpart, asciipart, c in HEX_LINES[:n]:
        d.text((78, y), off, font=font(13), fill=DIM)
        d.text((158, y), hexpart, font=font(13), fill=TEXT)
        d.text((320, y), asciipart, font=font(13), fill=c)
        y += 26

    # kutu diyagramı
    panel(d, [490, 80, 830, 300], "kutu yapısı")
    boxes = [("ftyp", DIM), ("ispe", GREEN), ("uncC", GREEN), ("iloc", YELLOW), ("mdat", RED)]
    x = 510
    for name, c in boxes:
        w = 52
        d.rounded_rectangle([x, 130, x + w, 170], radius=6, outline=c, width=2)
        d.text((x + 12, 142), name, font=font(15, bold=True), fill=c)
        x += w + 12
    d.text((510, 190), "ispe: «96 × 96 pikselim var»", font=font(15), fill=GREEN)
    d.text((510, 214), "  → 96 × 96 = 9216 bayt VAAT", font=font(15), fill=GREEN)
    d.text((510, 246), "mdat: yalnızca 96 bayt veri", font=font(15), fill=RED)
    if reveal > 0.55:
        d.rounded_rectangle([500, 238, 700, 268], radius=6, outline=RED, width=2)

    # oran çubuğu
    panel(d, [490, 320, 830, 420], "vaat vs gerçek")
    d.text((510, 348), "vaat edilen:", font=font(15), fill=DIM)
    d.rectangle([510, 368, 810, 388], fill="#21262d", outline=GREEN)
    d.rectangle([510, 368, 513 + int(297 * min(1.0, reveal)), 388], fill=GREEN)
    d.text((700, 366), "9216 B", font=font(13), fill=GREEN)
    d.text((510, 396 - 24 + 24), "gerçek:", font=font(15), fill=DIM)
    real_w = 3 + int(297 * 96 / 9216 * min(1.0, reveal * 1.2))
    d.rectangle([600, 394 - 24 + 22, 600 + real_w, 412 - 24 + 22], fill=RED)
    d.text((620 + real_w, 388), "96 B  (%1!)", font=font(13, bold=True), fill=RED)

    d.text((20, H - 34), "Decoder vaade inanır, gerçeği KONTROL ETMEZ →",
           font=font(15), fill=RED)
    return img


# ------------------------------------------------- sahne 3: libheif taşması
def scene_memcpy(progress: float):
    img, d = new_frame()
    header(d, 2, 5, "3 — libheif 1.17.6: sınır kontrolsüz kopyalama", ORANGE)

    panel(d, [60, 78, 830, 240], "libheif/uncompressed_image.cc : 756")
    d.text((80, 116), "uint32_t bytes_per_channel = width * height;",
           font=font(15), fill=CYAN)
    d.text((430, 116), "// 96 × 96 = 9216", font=font(15), fill=DIM)
    d.text((80, 146), "memcpy(dst, data.data(), bytes_per_channel);",
           font=font(15, bold=True), fill=TEXT)
    d.text((452, 146), "// data.size() = 96 !!", font=font(15, bold=True), fill=RED)
    d.text((80, 180), "// uzunluk, dosyadaki VERİYLE hiç karşılaştırılmıyor",
           font=font(13), fill=DIM)

    # buffer diyagramı
    panel(d, [60, 262, 830, 470], "bellekte ne oluyor?")
    y0 = 330
    d.text((80, y0 - 26), "data (std::vector):", font=font(15), fill=DIM)
    # yeşil: gerçek veri
    d.rectangle([80, y0, 240, y0 + 44], fill="#12351c", outline=GREEN, width=2)
    d.text((92, y0 + 6), "96 B", font=font(15, bold=True), fill=GREEN)
    d.text((92, y0 + 24), "dosya verisi", font=font(13), fill=GREEN)
    # kırmızı: OOB
    oob_w = int(560 * progress)
    if oob_w > 2:
        d.rectangle([242, y0, 242 + oob_w, y0 + 44], fill="#3d1214", outline=RED, width=2)
        if progress > 0.15:
            d.text((260, y0 + 6), "OOB READ", font=font(15, bold=True), fill=RED)
        if progress > 0.4:
            d.text((260, y0 + 24), "komşu HEAP → çıktıya kopyalanıyor", font=font(13), fill=RED)
    # ok
    d.text((80, y0 + 60), "memcpy", font=font(13, bold=True), fill=CYAN)
    arr_x = 170 + int(600 * progress)
    d.line([150, y0 + 74, arr_x, y0 + 74], fill=CYAN, width=3)
    d.polygon([(arr_x, y0 + 68), (arr_x + 12, y0 + 74), (arr_x, y0 + 80)], fill=CYAN)
    d.text((80, y0 + 92), "dst (9216 B piksel düzlemi)  ←  ilk 96 B meşru, kalanı KOMŞU BELLEK",
           font=font(13), fill=DIM)
    d.text((20, H - 34), "Sınır kontrolü yok = saldırgan okuma menzilini BELİRLİYOR  →",
           font=font(15), fill=ORANGE)
    return img


# --------------------------------------------------- sahne 4: heap sızıntısı
HEAP_ITEMS = [
    ("HEIST!", PURPLE), ("root_admin", RED), ("Sup3rS3cret!2026", YELLOW),
    ("FK-PROD-9f8a", GREEN), ("HEIST!", PURPLE), ("Bk!2026@db", CYAN),
    ("HEIST!", PURPLE), ("admin.internal", RED), ("HEIST!", PURPLE),
    ("FEYSBUK", GREEN), ("HEIST!", PURPLE), ("Sup3rS3cret", YELLOW),
]


def scene_heap(progress: float):
    img, d = new_frame()
    header(d, 3, 5, "4 — Komşu bellekte NE var? (heap grooming)", PURPLE)

    d.text((60, 74), "heifconv, çözme öncesi belleği gizli veriyle doldurur",
           font=font(15), fill=DIM)
    d.text((60, 96), "(gerçek sunucuların RAM'inde de sırlar YAŞAR)", font=font(15), fill=DIM)

    # heap şeridi
    y0, cell = 150, 64
    panel(d, [50, y0 - 34, 838, y0 + cell + 26], "heap")
    x = 62
    for i, (txt, c) in enumerate(HEAP_ITEMS):
        w = 12 * (6 if txt == "HEIST!" else max(8, len(txt)))
        copied = progress * 760 > (x - 50)
        fill = "#0d1117"
        if copied:
            fill = "#12351c"
        d.rectangle([x, y0, x + w - 6, y0 + cell - 20], fill=fill, outline=c, width=1)
        label = txt if len(txt) <= 12 else txt[:11]
        d.text((x + 4, y0 + 12), label, font=font(13, bold=(txt == "HEIST!")), fill=c if copied else DIM)
        x += w
        if x > 790:
            break

    # süpürme çizgisi
    sweep_x = 50 + int(788 * progress)
    if 0 < sweep_x < 838:
        d.line([sweep_x, y0 - 40, sweep_x, y0 + cell], fill=CYAN, width=3)
        d.text((min(sweep_x + 8, 700), y0 - 36), "memcpy →", font=font(13, bold=True), fill=CYAN)

    d.text((60, y0 + cell + 60), "9120 bayt komşu bellek okunuyor ve", font=font(17, bold=True), fill=TEXT)
    d.text((60, y0 + cell + 88), "çıktı GÖRÜNTÜSÜNÜN piksellerine yazılıyor…",
           font=font(17, bold=True), fill=TEXT)
    d.text((60, y0 + cell + 140), "HEIST! = groom işareti   ·   renkli kutular = bellekteki sırlar",
           font=font(13), fill=DIM)

    d.text((20, H - 34), "Bu, salt-okunur bir SOYGUN: hiçbir hata, hiçbir çökme yok  →",
           font=font(15), fill=PURPLE)
    return img


# ---------------------------------------------------- sahne 5: avatar dump
def scene_avatar(progress: float):
    img, d = new_frame()
    header(d, 4, 5, "5 — Profil fotoğrafı = sunucunun heap'i", GREEN)

    # piksel ızgarası
    gx, gy, cell = 80, 110, 4
    n_fill = int(96 * 96 * progress)
    rnd = random.Random(115)
    panel(d, [60, 90, 80 + 96 * cell + 20, 110 + 96 * cell + 20], None)
    for i in range(n_fill):
        px, py = i % 96, i // 96
        v = rnd.randint(0, 255)
        c = (v, v, v)
        d.rectangle([gx + px * cell, gy + py * cell, gx + px * cell + cell - 1, gy + py * cell + cell - 1], fill=c)
    if progress < 1.0:
        py = n_fill // 96
        px = n_fill % 96
        d.rectangle([gx + px * cell - 1, gy + py * cell - 1, gx + px * cell + cell, gy + py * cell + cell],
                    outline=CYAN, width=2)

    # yan panel
    panel(d, [560, 90, 830, 380], "avatar_1.bmp")
    d.text((578, 130), "kopyalanan:", font=font(15), fill=DIM)
    d.text((578, 152), f"{int(9216 * progress):>5} / 9216 bayt", font=font(20, bold=True), fill=CYAN)
    d.text((578, 196), "piksel değeri =", font=font(15), fill=DIM)
    d.text((578, 216), "heap baytı", font=font(20, bold=True), fill=TEXT)
    if progress > 0.55:
        d.text((578, 268), "içinde kaybolan:", font=font(15), fill=DIM)
        d.text((578, 290), "root_admin", font=font(15, bold=True), fill=RED)
        d.text((578, 312), "Sup3rS3cret!2026", font=font(15, bold=True), fill=RED)
        d.text((578, 334), "FK-PROD-9f8a…", font=font(15, bold=True), fill=RED)

    d.text((20, H - 34), "«Fotoğrafın hoş görünmüyor?» — Bu bir fotoğraf değil, DUMP  →",
           font=font(15), fill=GREEN)
    return img


# --------------------------------------------------- sahne 6: sızanın okunması
def scene_steal(progress: float):
    img, d = new_frame()
    header(d, 5, 6, "6 — Saldırgan avatarı indirir ve pikselleri çözer", RED)

    panel(d, [60, 80, 830, 300], "$ terminal")
    lines = [
        ("$ curl -s -b session 'download.php?f=avatars/avatar_1.bmp' -o avatar.bmp", TEXT),
        ("$ python fix_bmp.py avatar.bmp   # her 3. bayt = gri düzlem", DIM),
    ]
    y = 112
    for txt, c in lines:
        d.text((80, y), txt, font=font(15), fill=c)
        y += 26

    secrets = [
        "Kullanici adi : root_admin",
        "Sifre         : Sup3rS3cret!2026",
        "API anahtari  : FK-PROD-9f8a7b6c5d4e3f2a1b0c",
        "Yedek servisi : mysql://backup_svc:Bk!2026@db-internal",
    ]
    n = max(0, int(len(secrets) * min(1.0, (progress - 0.25) * 1.8)))
    y += 6
    for i in range(n):
        hl = 1.0 if progress > 0.75 else 0.55
        col = tuple(int(0.55 * 248 + 0) for _ in ()) if False else RED
        d.rounded_rectangle([70, y - 6, 620, y + 22], radius=4, fill="#2d1113")
        d.text((80, y), secrets[i], font=font(15, bold=True), fill=RED)
        y += 30

    panel(d, [60, 330, 830, 420], "neden bu kadar ağır?")
    d.text((80, 362), "Hiçbir hata yok. Hiçbir log yok. Sadece bir «fotoğraf».",
           font=font(15), fill=TEXT)
    d.text((80, 386), "Meta bu sınıfa $115.000 ödedi — RCE'ye kadar götürüldü.",
           font=font(15, bold=True), fill=YELLOW)

    d.text((20, H - 34), "Adli kanıt: bellek denetleyicisi aynı dosyada taşmayı RAPORLAR  →",
           font=font(15), fill=DIM)
    return img


# --------------------------------------------------------- sahne 7: ASAN + kapanış
def scene_asan(progress: float):
    img, d = new_frame()
    header(d, 6, 6, "7 — Kanıt: AddressSanitizer", RED)
    panel(d, [60, 80, 830, 260], "heifconv-asan crash.heic")
    lines = [
        ("==40==ERROR: AddressSanitizer: heap-buffer-overflow", RED),
        ("READ of size 9216 at 0x5080… thread T0", TEXT),
        ("  #1 UncompressedImageCodec::decode_uncompressed_image", DIM),
        ("    libheif/uncompressed_image.cc:756", CYAN),
        ("0x5080… is located 0 bytes after 96-byte region", TEXT),
    ]
    n = max(1, int(len(lines) * min(1.0, progress * 1.3)))
    y = 118
    for i in range(n):
        txt, c = lines[i]
        d.text((80, y), txt, font=font(14, bold=(i == 0)), fill=c)
        y += 26

    # kapanış
    t = max(0.0, (progress - 0.45) / 0.55)
    if t > 0:
        d.text((60, 300 + int((1 - t) * 30)), "HEIF HEIST — yeniden üretildi.",
               font=font(30, bold=True), fill=TEXT)
        d.text((60, 350), "Gerçek olay: Meta (Facebook/Instagram), Eylül 2026 — ödül:", font=font(17), fill=DIM)
        d.text((60, 374), "$115.000", font=font(40, bold=True), fill=GREEN)
        d.text((60, 436), "github.com/Rollingzzzzz/heif-heist-lab", font=font(17, bold=True), fill=CYAN)
        d.text((60, 462), "docker compose up -d --build   →   python exploit/heif_exploit.py",
               font=font(15), fill=DIM)
    return img


# ---------------------------------------------------------------- birleştir
def ease(x):
    return x * x * (3 - 2 * x)


def main():
    frames = []
    SUB = 10  # sahne başına kare
    for i in range(SUB):
        frames.append(scene_upload(ease(i / (SUB - 1))))
    for i in range(SUB + 2):
        frames.append(scene_bytes(ease(i / (SUB + 1))))
    for i in range(SUB + 2):
        frames.append(scene_memcpy(ease(i / (SUB + 1))))
    for i in range(SUB + 2):
        frames.append(scene_heap(i / (SUB + 1)))          # süpürme doğrusal
    for i in range(SUB + 2):
        frames.append(scene_avatar(i / (SUB + 1)))
    for i in range(SUB + 2):
        frames.append(scene_steal(min(1.0, i / (SUB - 1))))
    for i in range(SUB + 4):
        frames.append(scene_asan(min(1.0, i / (SUB + 1))))

    out_dir = Path(__file__).resolve().parents[1] / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "heif-heist-flow.gif"

    # P moduna çevir (palet optimize)
    pframes = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    pframes[0].save(
        out, save_all=True, append_images=pframes[1:],
        duration=140, loop=0, optimize=True,
    )
    kb = out.stat().st_size / 1024
    print(f"OK: {out}  ({len(pframes)} kare, {kb:.0f} KB)")

    # önizleme kareleri (QA)
    for idx in (0, 12, 24, 36, 48, 58, len(frames) - 1):
        frames[idx].save(out_dir / f"_preview_{idx:02d}.png")
    print("önizlemeler: _preview_*.png")


if __name__ == "__main__":
    main()
