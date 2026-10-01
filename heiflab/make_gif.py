#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_gif.py — HEIF Heist laboratuvarının akışını anlatan GIF üretici.

Sahne: GitHub-dark estetiği, monospace font. Anlatım: crafted HEIC yüklenir →
libheif sınır kontrolsüz memcpy → komşu heap avatarın piksellerine sızar →
saldırgan profil fotoğrafından yönetici şifresini okur.

Çıktı: docs/gif/heist-flow.gif (sonsuz döngü)
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540
BG     = (13, 17, 23)
PANEL  = (22, 27, 34)
BORDER = (48, 54, 61)
GREEN  = (63, 185, 80)
RED    = (248, 81, 73)
BLUE   = (88, 166, 255)
YELLOW = (210, 153, 34)
PURPLE = (188, 140, 255)
TEXT   = (201, 209, 217)
DIM    = (139, 148, 158)

FD = "C:/Windows/Fonts/consola.ttf"
FB = "C:/Windows/Fonts/consolab.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else FD, size)


F_T1   = font(34, True)
F_T2   = font(19)
F_H    = font(22, True)
F_B    = font(19)
F_S    = font(16)
F_XS   = font(14)
F_CODE = font(19)
F_BIG  = font(26, True)


def canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 64], fill=PANEL)
    d.line([0, 64, W, 64], fill=BORDER, width=2)
    d.text((24, 14), "HEIF Heist", font=F_T1, fill=RED)
    tw = d.textlength("HEIF Heist", font=F_T1)
    d.text((24 + tw + 20, 24),
           "tek bir HEIC yükleme — Meta'nın 115.000 $ ödediği sınıf",
           font=F_T2, fill=DIM)
    return img, d


def panel(d, xy, title=None, color=BORDER):
    x0, y0, x1, y1 = xy
    d.rectangle(xy, fill=PANEL, outline=color, width=2)
    if title:
        d.text((x0 + 14, y0 + 10), title, font=F_H, fill=color)


def arrow(d, x0, y0, x1, y1, color=BLUE, w=3):
    d.line([x0, y0, x1, y1], fill=color, width=w)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (2.6, -2.6):
        d.line([x1, y1, x1 + 14 * math.cos(ang + da), y1 + 14 * math.sin(ang + da)],
               fill=color, width=w)


frames = []


def add(img, ms):
    frames.append((img, ms))


# ===================================================== SAHNE 1 — dosya
img, d = canvas()
d.text((24, 90), "[1]  SALDIRGAN — crafted dosyayı üretir (craft_heic.py)", font=F_H, fill=BLUE)
panel(d, (24, 140, 460, 410), "gunun-karesi.heic   (385 bayt)", BLUE)
d.text((44, 192), "ftyp  mif1 / heic / unci", font=F_CODE, fill=TEXT)
d.text((44, 224), "meta  hdlr pitm iinf('unci')", font=F_CODE, fill=TEXT)
d.text((44, 256), "ispe : 96 x 96", font=F_CODE, fill=RED)
d.text((260, 256), "<-- YALAN", font=F_CODE, fill=RED)
d.text((44, 288), "cmpd : monochrome", font=F_CODE, fill=TEXT)
d.text((44, 320), "uncC : planar (interleave=0)", font=F_CODE, fill=TEXT)
d.text((44, 352), "mdat : [HEIST-SECRET-PAGE-...]", font=F_CODE, fill=YELLOW)
d.text((44, 384), "veri : 96 bayt", font=F_CODE, fill=YELLOW)
d.text((200, 384), "<-- GERÇEK", font=F_CODE, fill=YELLOW)
panel(d, (500, 140, 936, 410), "decoder'a söylenen vs gerçek", RED)
d.text((520, 192), "ilan edilen piksel : 96 x 96", font=F_B, fill=TEXT)
d.text((520, 224), "ilan edilen boyut  : 9216 bayt", font=F_B, fill=TEXT)
d.text((520, 272), "gerçek veri        : 96 bayt", font=F_B, fill=TEXT)
d.text((520, 304), "fark               : 9120 bayt", font=F_B, fill=RED)
d.text((520, 356), "fazla okunacak yer:", font=F_H, fill=RED)
d.text((520, 386), "KOMŞU HEAP", font=F_BIG, fill=RED)
d.text((24, 446), "Dosya geçerli bir HEIF kutu yapısı taşıyor — sunucu bunu iPhone fotoğrafı zannediyor.",
       font=F_S, fill=DIM)
add(img, 1700)

# ===================================================== SAHNE 2 — yükleme
img, d = canvas()
d.text((24, 90), "[2]  YÜKLEME — 'Profil Fotoğrafı (HEIC)' kartı → pipeline", font=F_H, fill=BLUE)
panel(d, (24, 150, 260, 330), "SALDIRGAN", BLUE)
d.text((44, 210), "demo@feysbuk.test", font=F_B, fill=TEXT)
d.text((44, 244), "sıradan kullanıcı", font=F_S, fill=DIM)
d.text((44, 280), "yetki: YOK", font=F_B, fill=RED)
arrow(d, 264, 240, 354, 240, GREEN)
d.text((272, 210), "POST", font=F_S, fill=GREEN)
panel(d, (358, 130, 936, 350), "FEYSBUK SUNUCUSU  (Docker)", GREEN)
d.text((378, 182), "upload.php", font=F_CODE, fill=TEXT)
d.text((398, 216), "└ heifconv foto.heic → avatar_1.bmp", font=F_CODE, fill=TEXT)
d.text((418, 250), "└ libheif 1.17.6 — CVE-2025-46087 YAŞAR", font=F_CODE, fill=RED)
d.text((418, 284), "└ --secret-file secret/admin_credentials.txt", font=F_S, fill=YELLOW)
d.text((418, 312), "  (pipeline belleğinde gizli yönetici verisi yaşar)", font=F_S, fill=DIM)
panel(d, (358, 380, 936, 470), "yani", YELLOW)
d.text((378, 424), "gerçek sunucular gibi: sırlar RAM'de duruyor", font=F_B, fill=YELLOW)
d.text((24, 500), "Yükleme tamamen meşru görünüyor: HTTP 200, 'dönüştürüldü'. Sunucu hiçbir şeyden şüphelenmiyor.",
       font=F_S, fill=DIM)
add(img, 1700)

# ===================================================== SAHNE 3 — hatalı kod
img, d = canvas()
d.text((24, 90), "[3]  KÖK NEDEN — libheif 1.17.6, uncompressed_image.cc:756", font=F_H, fill=RED)
panel(d, (24, 140, 936, 300), "UncompressedImageCodec::decode_uncompressed_image()", RED)
d.text((44, 186), "uint32_t bytes_per_channel = width * height;", font=F_CODE, fill=TEXT)
d.text((44, 218), "memcpy(dst, uncompressed_data.data(), bytes_per_channel);", font=F_CODE, fill=RED)
d.text((44, 252), "// uzunluk VERİDEN değil İSPE'DEN — kontrol YOK", font=F_CODE, fill=YELLOW)
panel(d, (24, 330, 936, 470), "matematik", BLUE)
d.text((44, 378), "kopyalanacak : 9216 bayt", font=F_B, fill=TEXT)
d.text((44, 412), "elde var     : 96 bayt (vector)", font=F_B, fill=TEXT)
d.text((500, 372), "eksik  : 9120 bayt", font=F_BIG, fill=RED)
d.text((500, 414), "kaynak : komşu heap bellek", font=F_B, fill=RED)
d.text((24, 496), "Buffer sorunu işte bu: uzunluk doğrulaması olmayan tek bir memcpy.", font=F_S, fill=DIM)
add(img, 1700)

# ===================================================== SAHNE 4 — heap süpürme (animasyon)
heap_layout = [
    ("vector",  BLUE,  "HEIST-SECRET-PAGE- ... (dosyadaki 96 B)"),
    ("gizli-1", RED,   "### FEYSBUK-SECRET: admin_credentials.txt"),
    ("gizli-2", RED,   "Yonetim paneli: https://admin.internal..."),
    ("gizli-3", RED,   "Kullanici adi: root_admin"),
    ("gizli-4", RED,   "Sifre        : Sup3rS3cret!2026"),
    ("gizli-5", RED,   "API anahtari : FK-PROD-9f8a7b6c5d4e3f2a"),
    ("gizli-6", RED,   "Yedek servisi: mysql://backup_svc:Bk!2026@..."),
    ("gizli-7", RED,   "UYARI: Bu dosyanin disina cikmasi YASAKTIR."),
    ("pad",     DIM,   "............ (grooming pad) ............"),
]
for upto in [2, 4, 6, 8]:
    img, d = canvas()
    d.text((24, 90), "[4]  HEIST — memcpy, 96 baytlık vektörden 9216 bayt SÜPÜRÜYOR", font=F_H, fill=YELLOW)
    panel(d, (24, 140, 936, 432), "heap  (adres artışı →)", YELLOW)
    y = 176
    x0 = 44
    for i, (name, colr, content) in enumerate(heap_layout):
        read = i <= upto
        h = 24
        fill = (46, 28, 24) if (read and colr == RED) else PANEL
        d.rectangle([x0, y, x0 + 218, y + h], fill=fill,
                    outline=(colr if read else BORDER), width=2)
        d.text((x0 + 8, y + 3), name, font=F_XS, fill=colr if read else DIM)
        if read and colr == RED:
            d.text((x0 + 150, y + 3), "OKUNDU", font=F_XS, fill=RED)
        d.text((x0 + 240, y + 3), content, font=F_S, fill=TEXT if read else DIM)
        y += h + 4
    okunan = 96 + 96 * min(upto, 7)
    d.text((44, 444), f"memcpy ilerlemesi: {min(okunan + 96, 9216)} / 9216 bayt", font=F_B, fill=YELLOW)
    d.text((520, 440), "sınır YOK — komşuluk yeterli", font=F_H, fill=RED)
    d.text((24, 496), "Saldırganın grooming'i sayesinde komşuluk tesadüf değil: sızan bölge BİLİNÇLİ olarak gizli dosyayla dolu.",
           font=F_S, fill=DIM)
    add(img, 550)

# ===================================================== SAHNE 5 — avatar = heap dump
img, d = canvas()
d.text((24, 90), "[5]  SONUÇ — 'profil fotoğrafı' artık sunucu belleğinin karesi", font=F_H, fill=GREEN)
panel(d, (24, 140, 320, 450), "avatar_1.bmp  (96x96)", GREEN)
random.seed(7)
for py in range(96):
    for px in range(0, 96, 3):
        v = random.choice([0, 0, 0, 0, 30, 60, 200, 230]) if py % 8 else random.choice([90, 120])
        d.rectangle([44 + px * 2.4, 186 + py * 2.4, 44 + px * 2.4 + 7, 186 + py * 2.4 + 2],
                    fill=(v, v, v))
d.text((40, 420), "içindeki bantlar '=' satırları", font=F_XS, fill=YELLOW)
arrow(d, 330, 295, 420, 295, GREEN)
panel(d, (424, 140, 936, 450), "piksellerden baytlara geri dönüşüm", BLUE)
d.text((444, 192), "BMP pikselleri 3'e katlanmış gri;", font=F_B, fill=TEXT)
d.text((444, 222), "her 3. bayt = decoder düzlemi = sızan heap", font=F_B, fill=TEXT)
d.text((444, 268), "GET /download.php?f=avatars/avatar_1.bmp", font=F_CODE, fill=BLUE)
d.text((444, 304), "plane+337 :  root_admin", font=F_CODE, fill=RED)
d.text((444, 334), "plane+367 :  Sup3rS3cret!2026", font=F_CODE, fill=RED)
d.text((444, 364), "plane+1023:  FK-PROD-9f8a...", font=F_CODE, fill=RED)
d.text((444, 410), "Hata yok. Çökme yok.", font=F_H, fill=YELLOW)
d.text((444, 438), "Sadece bir 'profil fotoğrafı'.", font=F_H, fill=YELLOW)
d.text((24, 496), "Sunucu saldırgana kendi belleğini BMP olarak teslim etti.", font=F_S, fill=DIM)
add(img, 1900)

# ===================================================== SAHNE 6 — kanıt + yama
img, d = canvas()
d.text((24, 90), "[6]  KANIT + YAMA — aynı dosya, ASAN derlemesi", font=F_H, fill=PURPLE)
panel(d, (24, 140, 936, 330), "AddressSanitizer", PURPLE)
d.text((44, 184), "ERROR: AddressSanitizer: heap-buffer-overflow", font=F_CODE, fill=RED)
d.text((44, 216), "READ of size 9216 ... 0 bytes after 96-byte region", font=F_CODE, fill=TEXT)
d.text((44, 248), "#1 UncompressedImageCodec::decode_uncompressed_image", font=F_CODE, fill=DIM)
d.text((44, 280), "      libheif/uncompressed_image.cc:756", font=F_CODE, fill=DIM)
panel(d, (24, 360, 460, 470), "yama", GREEN)
d.text((44, 404), "libheif >= 1.18.0 (issue #1508)", font=F_B, fill=TEXT)
d.text((44, 436), "veya decoder'ı baştan engelle", font=F_B, fill=TEXT)
panel(d, (500, 360, 936, 470), "gerçek olay", RED)
d.text((520, 404), "HEIF Heist: aynı sınıf FB/IG'de RCE'ye kadar", font=F_B, fill=TEXT)
d.text((520, 436), "Meta ödülü: $115.000", font=F_BIG, fill=YELLOW)
d.text((24, 500), "github.com/Rollingzzzzz/heif-heist-lab  ·  heif-heist.com  ·  YALNIZCA İZOLE LAB İÇİN",
       font=F_S, fill=DIM)
add(img, 2000)

# ---------------------------------------------------------------- yaz
os.makedirs("docs/gif", exist_ok=True)
imgs = [f for f, _ in frames]
durations = [ms for _, ms in frames]
imgs[0].save(
    "docs/gif/heist-flow.gif",
    save_all=True,
    append_images=imgs[1:],
    duration=durations,
    loop=0,
    optimize=True,
)
size_kb = os.path.getsize("docs/gif/heist-flow.gif") // 1024
print(f"OK: docs/gif/heist-flow.gif  ({len(frames)} kare, {size_kb} KB, {W}x{H})")
