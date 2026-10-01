#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_gif.py — HEIF Heist akış GIF'i (UI odaklı anlatım).
Hikâye: feysbuk'a giriş → HEIC yükle → (arka planda libheif taşması) →
profil fotoğrafına tıkla → içindeki şifre ortaya çıkar.

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
APPBG   = "#f0f2f5"          # feysbuk sayfa arka planı (açık tema)
CARDBG  = "#ffffff"
APPBORD = "#dddfe2"
APPTXT  = "#1c1e21"
APPDIM  = "#65676b"

BX0, BY0, BX1, BY1 = 70, 84, 810, 508   # tarayıcı mockup çerçevesi

_F_CACHE = {}


def _truetype(size, bold):
    key = (size, bold)
    if key not in _F_CACHE:
        name = "consolab.ttf" if bold else "consola.ttf"
        _F_CACHE[key] = ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
    return _F_CACHE[key]


def font(size, bold=False):
    return _truetype(size, bold)


random.seed(115000)


def new_frame():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def header(d, step, total, title, color=CYAN):
    d.rectangle([0, 0, W, 54], fill=PANEL)
    d.line([0, 54, W, 54], fill=BORDER, width=1)
    d.text((20, 15), title, font=font(20, bold=True), fill=color)
    x = W - 20
    for i in range(total - 1, -1, -1):
        c = color if i <= step else BORDER
        d.ellipse([x - 14, 20, x, 34], fill=c)
        x -= 20
    d.text((20, 34), "heif-heist-lab", font=font(13), fill=DIM)


def footer(d, text, color):
    d.text((20, H - 34), text, font=font(15), fill=color)


def browser(d, url):
    """Tarayıcı çerçevesi + URL çubuğu. İçini çağıran doldurur."""
    d.rounded_rectangle([BX0, BY0, BX1, BY1], radius=10, fill=APPBG, outline=BORDER)
    d.rounded_rectangle([BX0, BY0, BX1, BY0 + 60], radius=10, fill=PANEL)
    d.rectangle([BX0, BY0 + 34, BX1, BY0 + 60], fill=PANEL)
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        d.ellipse([BX0 + 14 + i * 22, BY0 + 12, BX0 + 26 + i * 22, BY0 + 24], fill=c)
    d.rounded_rectangle([BX0 + 92, BY0 + 9, BX1 - 14, BY0 + 29], radius=12, fill=BG, outline=BORDER)
    d.text((BX0 + 106, BY0 + 11), url, font=font(13), fill=DIM)


def app_topbar(d, y0, noisy_avatar=False):
    """feysbuk mavi üst barı (girişli hal)."""
    d.rectangle([BX0, y0, BX1, y0 + 42], fill=FBBLUE)
    d.text((BX0 + 20, y0 + 7), "feysbuk", font=font(24, bold=True), fill="#ffffff")
    # avatar + isim + çıkış
    ax, ay = BX1 - 262, y0 + 5
    if noisy_avatar:
        paste_noise_circle(d, ax, ay, 32, seed=7)
    else:
        d.ellipse([ax, ay, ax + 32, ay + 32], fill="#e4e6eb")
    d.text((ax + 42, ay + 8), "Demo Kullanıcı", font=font(14, bold=True), fill="#ffffff")
    d.rounded_rectangle([BX1 - 84, y0 + 6, BX1 - 14, y0 + 34], radius=6, fill="#ffffff")
    d.text((BX1 - 74, y0 + 12), "Çıkış", font=font(14, bold=True), fill=FBBLUE)


def cursor(d, x, y, click=0.0):
    if click > 0:
        r = 6 + 18 * click
        w = max(1, int(3 * (1 - click)))
        d.ellipse([x - r, y - r, x + r, y + r], outline=CYAN, width=w)
    pts = [(x, y), (x, y + 18), (x + 4.5, y + 13.5), (x + 8, y + 21),
           (x + 11.5, y + 19.5), (x + 8, y + 12), (x + 14, y + 12)]
    d.polygon(pts, fill="#ffffff", outline="#000000")


def paste_noise_circle(d, cx, cy, size, seed, coverage=1.0):
    """dairesel gürültü avatar (offscreen üret + maskele)."""
    rnd = random.Random(seed)
    tile = Image.new("RGB", (size, size), "#e4e6eb")
    td = ImageDraw.Draw(tile)
    n = int((size // 2) ** 2 * coverage)
    for i in range(n):
        px, py = i % (size // 2), i // (size // 2)
        v = rnd.randint(0, 255)
        td.rectangle([px * 2, py * 2, px * 2 + 1, py * 2 + 1], fill=(v, v, v))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    d._image.paste(tile, (cx, cy), mask)


def noise_rect(d, x0, y0, w, h, cell, seed, coverage=1.0):
    rnd = random.Random(seed)
    cols, rows = max(1, w // cell), max(1, h // cell)
    n = int(cols * rows * coverage)
    for i in range(n):
        px, py = i % cols, i // cols
        v = rnd.randint(0, 255)
        d.rectangle([x0 + px * cell, y0 + py * cell,
                     x0 + px * cell + cell - 1, y0 + py * cell + cell - 1],
                    fill=(v, v, v))


# ------------------------------------------------------- sahne 1: giriş
def scene_login(progress):
    img, d = new_frame()
    header(d, 0, 6, "1 — feysbuk'a giriş: sıradan bir kullanıcı", CYAN)
    browser(d, "http://feysbuk.test/")

    # marka
    d.text((BX0 + 60, 200), "feysbuk", font=font(54, bold=True), fill=FBBLUE)
    d.text((BX0 + 64, 268), "Feysbuk, tanıdıklarınızla bağlantıda", font=font(17), fill=APPTXT)
    d.text((BX0 + 64, 292), "kalmanın kolay yoludur.", font=font(17), fill=APPTXT)

    # login kartı
    card = [BX0 + 420, 150, BX1 - 60, 380]
    d.rounded_rectangle(card, radius=10, fill=CARDBG, outline=APPBORD)
    d.rounded_rectangle([card[0] + 18, card[1] + 20, card[0] + 280, card[1] + 58],
                        radius=6, fill="#f5f6f7", outline=APPBORD)
    d.text((card[0] + 30, card[1] + 30), "demo@feysbuk.test", font=font(15), fill=APPTXT)
    d.rounded_rectangle([card[0] + 18, card[1] + 70, card[0] + 280, card[1] + 108],
                        radius=6, fill="#f5f6f7", outline=APPBORD)
    d.text((card[0] + 30, card[1] + 80), "••••••••", font=font(15), fill=APPTXT)
    btn = [card[0] + 18, card[1] + 122, card[0] + 280, card[1] + 162]
    d.rounded_rectangle(btn, radius=6, fill=FBBLUE)
    d.text((btn[0] + 88, btn[1] + 12), "Giriş Yap", font=font(17, bold=True), fill="#ffffff")

    # imleç butona gider + tıklar
    cx, cy = btn[0] + 140, btn[1] + 22
    mx = BX1 - 100 + int((cx - (BX1 - 100)) * min(1.0, progress * 1.3))
    my = 420 + int((cy - 420) * min(1.0, progress * 1.3))
    click = max(0.0, (progress - 0.75) / 0.25)
    cursor(d, mx, my, click)

    footer(d, "Hiçbir özel yetkisi yok — test veritabanında admin değil.", CYAN)
    return img


# -------------------------------------------------- sahne 2: yükleme
def scene_upload(progress):
    img, d = new_frame()
    header(d, 1, 6, "2 — Profil fotoğrafı yükleniyor: gunun-karesi.heic", CYAN)
    browser(d, "http://feysbuk.test/home.php")
    app_topbar(d, BY0 + 60)

    # yükleme kartı
    card = [BX0 + 130, BY0 + 122, BX1 - 130, BY0 + 350]
    d.rounded_rectangle(card, radius=10, fill=CARDBG, outline=APPBORD)
    d.text((card[0] + 20, card[1] + 14), "Profil Fotoğrafı (HEIC)",
           font=font(17, bold=True), fill=APPTXT)

    fs = [card[0] + 20, card[1] + 52, card[0] + 380, card[1] + 88]
    d.rectangle(fs, fill="#f5f6f7", outline=APPBORD)
    d.rectangle([fs[0], fs[1], fs[0] + 100, fs[1] + 36], fill="#e4e6eb")
    d.text((fs[0] + 10, fs[1] + 10), "Choose File", font=font(13), fill=APPTXT)
    d.text((fs[0] + 112, fs[1] + 10), "gunun-karesi.heic", font=font(13), fill=GREEN)

    btn = [card[0] + 20, card[1] + 108, card[0] + 220, card[1] + 148]
    uploading = progress > 0.62
    d.rounded_rectangle(btn, radius=6, fill=FBBLUE)
    d.text((btn[0] + 34, btn[1] + 12), "Yükle ve Dönüştür", font=font(15, bold=True), fill="#ffffff")

    # ilerleme çubuğu
    if uploading:
        pb = [card[0] + 20, card[1] + 168, card[0] + 380, card[1] + 188]
        d.rounded_rectangle(pb, radius=4, fill="#e4e6eb")
        fillw = int((pb[2] - pb[0]) * ((progress - 0.62) / 0.38))
        d.rounded_rectangle([pb[0], pb[1], pb[0] + fillw, pb[3]], radius=4, fill=FBBLUE)
        d.text((pb[0], pb[3] + 8), "Sunucuda dönüştürülüyor… (libheif 1.17.6)",
               font=font(13), fill=APPDIM)

    d.text((card[0] + 20, card[3] - 36),
           "Dosya sunucuda heifconv pipeline'ı ile işlenir.",
           font=font(13), fill=APPDIM)

    cx, cy = btn[0] + 110, btn[1] + 20
    mx = BX1 - 150 + int((cx - (BX1 - 150)) * min(1.0, progress * 1.5))
    my = 300 + int((cy - 300) * min(1.0, progress * 1.5))
    click = max(0.0, (progress - 0.55) / 0.2) if not uploading else 0.0
    cursor(d, mx, my, click)

    footer(d, "Yükleme NORMAL görünüyor: «başarıyla dönüştürüldü».", CYAN)
    return img


# --------------------------------------- sahne 3: arka planda ne oluyor?
def scene_background(progress):
    img, d = new_frame()
    header(d, 2, 6, "3 — Arka planda sunucuda NE oluyor?", ORANGE)

    d.text((BX0 + 10, 70), "kullanıcı bunu GÖRMEZ — üç adım, milisaniyeler içinde:",
           font=font(15), fill=DIM)

    steps = [
        ("1 · SAHTE DOSYA", [
            "«96×96 pikselim var»",  "",
            "vaat: 96×96 = 9216 B",  "gerçek veri: 96 B",
        ], YELLOW, "VAAT: 9216 B · GERÇEK: 96 B"),
        ("2 · libheif 1.17.6", [
            "memcpy(dst, data, 9216)", "",
            "uzunluk KONTROLSÜZ →",   "9120 B komşu heap okunur",
        ], RED, "HEAP-BUFFER-OVERFLOW"),
        ("3 · çıktı görüntüsü", [
            "kopyalanan her bayt,",   "AVATARIN pikseline yazılır",
            "",                       "avatar = bellek dökümü",
        ], PURPLE, "avatar_1.bmp"),
    ]

    x = BX0 + 10
    cw = 232
    for i, (title, lines, c, tag) in enumerate(steps):
        appear = min(1.0, max(0.0, (progress - i * 0.22) * 3.5))
        if appear <= 0:
            x += cw + 14
            continue
        y0 = 110 - int((1 - appear) * 24)
        box = [x, y0, x + cw - 14, y0 + 250]
        d.rounded_rectangle(box, radius=10, fill=PANEL, outline=c, width=2)
        d.text((box[0] + 14, box[1] + 12), title, font=font(15, bold=True), fill=c)
        ly = box[1] + 48
        for line in lines:
            if line:
                d.text((box[0] + 14, ly), line, font=font(13), fill=TEXT if not line.startswith(("vaat", "gerçek")) else DIM)
            ly += 22
        if appear > 0.8:
            d.rounded_rectangle([box[0] + 14, box[3] - 44, box[0] + cw - 28, box[3] - 14],
                                radius=6, fill=BG, outline=c)
            d.text((box[0] + 22, box[3] - 38), tag, font=font(12, bold=True), fill=c)
        x += cw + 14

        # oklar
        if i < 2 and progress > (i + 1) * 0.22 + 0.08:
            ax0, ax1 = x - 12, x + 2
            ay = 230
            d.line([ax0, ay, ax1, ay], fill=ORANGE, width=3)
            d.polygon([(ax1, ay - 5), (ax1 + 8, ay), (ax1, ay + 5)], fill=ORANGE)

    footer(d, "Tek suçlu satır: memcpy uzunluğunu DOSYADAKİ VERİYLE karşılaştırmıyor.", ORANGE)
    return img


# --------------------------------------------- sahne 4: avatar güncellendi
def scene_updated(progress):
    img, d = new_frame()
    header(d, 3, 6, "4 — «Profil fotoğrafın güncellendi» — her şey normal görünüyor", GREEN)
    browser(d, "http://feysbuk.test/home.php")
    app_topbar(d, BY0 + 60, noisy_avatar=(progress > 0.25))

    card = [BX0 + 130, BY0 + 122, BX1 - 130, BY0 + 350]
    d.rounded_rectangle(card, radius=10, fill=CARDBG, outline=APPBORD)
    d.text((card[0] + 20, card[1] + 14), "Profil Fotoğrafı (HEIC)",
           font=font(17, bold=True), fill=APPTXT)

    # avatar öngörüntüsü (gürültü yavaş yavaş dolar)
    tx, ty = card[0] + 20, card[1] + 52
    d.rounded_rectangle([tx - 4, ty - 4, tx + 104, ty + 104], radius=6,
                        fill="#e4e6eb", outline=APPBORD)
    noise_rect(d, tx, ty, 96, 96, 3, seed=115, coverage=min(1.0, progress * 1.4))

    d.text((tx + 130, ty + 6), "gunun-karesi.heic → avatar_1.bmp", font=font(15), fill=APPTXT)
    if progress > 0.35:
        d.rounded_rectangle([tx + 130, ty + 40, tx + 400, ty + 70], radius=6, fill="#e7f5e9")
        d.text((tx + 142, ty + 47), "[OK] Profil fotoğrafın güncellendi", font=font(15, bold=True), fill=GREEN)
    if progress > 0.6:
        d.text((tx + 130, ty + 90), "Kimse bir şey fark etmedi.", font=font(15), fill=APPDIM)
        d.text((tx + 130, ty + 114), "Ama bu ARTIK bir fotoğraf değil…", font=font(15, bold=True), fill=RED)

    footer(d, "Avatar, sunucuda yeni üretilen avatar_1.bmp ile değişti.", GREEN)
    return img


# ------------------------------------------------ sahne 5: tıkla ve büyüt
def scene_click(progress):
    img, d = new_frame()
    header(d, 4, 6, "5 — Kullanıcı profil fotoğrafına TIKLIYOR…", CYAN)
    browser(d, "http://feysbuk.test/home.php")
    app_topbar(d, BY0 + 60, noisy_avatar=True)

    card = [BX0 + 130, BY0 + 122, BX1 - 130, BY0 + 350]
    d.rounded_rectangle(card, radius=10, fill=CARDBG, outline=APPBORD)
    d.text((card[0] + 20, card[1] + 14), "Profil Fotoğrafı (HEIC)",
           font=font(17, bold=True), fill=APPTXT)
    tx, ty = card[0] + 20, card[1] + 52
    noise_rect(d, tx, ty, 96, 96, 3, seed=115)

    # tıklama + modal
    cx, cy = tx + 48, ty + 48
    move = min(1.0, progress * 1.6)
    mx = BX1 - 200 + int((cx - (BX1 - 200)) * move)
    my = 300 + int((cy - 300) * move)
    click = max(0.0, (progress - 0.55) / 0.25)

    if progress > 0.6:
        overlay = int(200 * min(1.0, (progress - 0.6) / 0.3))
        d.rectangle([BX0, BY0 + 60, BX1, BY1], fill=(13, 17, 23))
        d.rectangle([BX0, BY0 + 60, BX1, BY1], fill=(13, 17, 23))
        # büyütülmüş avatar
        zx, zy = BX0 + 40, BY0 + 90
        d.rectangle([zx - 6, zy - 6, zx + 288 + 6, zy + 288 + 6], fill="#000000", outline=BORDER)
        noise_rect(d, zx, zy, 288, 288, 6, seed=115)
        d.text((zx, zy + 300), "avatar_1.bmp — 96×96, %4900 büyütülmüş", font=font(13), fill=DIM)
        # tarama çizgisi
        sx = zx + int(288 * ((progress - 0.6) / 0.4))
        if zx < sx < zx + 288:
            d.line([sx, zy, sx, zy + 288], fill=CYAN, width=2)
    cursor(d, mx, my, click)

    footer(d, "Görüntü büyütülüyor — piksellerin içinde BİR ŞEYLER yazıyor gibi…", CYAN)
    return img


# ------------------------------------------------- sahne 6: şifre ortaya çıkar
def scene_reveal(progress):
    img, d = new_frame()
    header(d, 5, 6, "6 — Bu görüntünün içinde: SUNUCUNUN BELLEĞİ", RED)
    browser(d, "http://feysbuk.test/download.php?f=avatars/avatar_1.bmp")

    # büyük gürültülü görsel solda
    zx, zy = BX0 + 30, BY0 + 92
    d.rectangle([zx - 6, zy - 6, zx + 288 + 6, zy + 288 + 6], fill="#000000", outline=BORDER)
    noise_rect(d, zx, zy, 288, 288, 6, seed=115)
    sx = zx + int(288 * min(1.0, progress * 1.2))
    if zx < sx < zx + 288:
        d.line([sx, zy, sx, zy + 288], fill=CYAN, width=2)
    d.text((zx, zy + 300), "avatar_1.bmp", font=font(13), fill=DIM)

    # sağda çözülen sırlar
    panel = [BX0 + 360, BY0 + 92, BX1 - 24, BY0 + 380]
    d.rounded_rectangle(panel, radius=10, fill=PANEL, outline=RED)
    d.text((panel[0] + 16, panel[1] + 12), "piksellerdeki baytlar (gri düzlem):",
           font=font(14), fill=DIM)
    secrets = [
        ("Kullanıcı adı : root_admin", False),
        ("Şifre         : Sup3rS3cret!2026", True),
        ("API anahtarı  : FK-PROD-9f8a7b6c…", False),
        ("Yedek DB      : backup_svc:Bk!2026", False),
    ]
    n = max(0, int(len(secrets) * min(1.0, progress * 1.35)))
    y = panel[1] + 44
    for i in range(n):
        text, hot = secrets[i]
        if hot and progress > 0.55:
            d.rounded_rectangle([panel[0] + 10, y - 7, panel[2] - 10, y + 21],
                                radius=5, fill="#3d1214", outline=RED, width=2)
        d.text((panel[0] + 18, y), text, font=font(15, bold=hot),
               fill=RED if hot else TEXT)
        y += 34

    d.text((panel[0] + 16, panel[3] - 34), "← bunlar sunucunun RAM'inden geldi",
           font=font(13), fill=DIM)

    footer(d, "Şifre, profil fotoğrafının GÖRSELİNİN içindeydi.", RED)
    return img


# --------------------------------------------------------- sahne 7: kapanış
def scene_outro(progress):
    img, d = new_frame()
    header(d, 6, 6, "7 — HEIF Heist: tek bir yükleme, çalınan bellek", GREEN)
    d.text((60, 110), "Profil fotoğrafın =", font=font(24), fill=DIM)
    d.text((60, 140), "sunucunun belleğinin karesi.", font=font(24, bold=True), fill=TEXT)

    # küçük avatar + şifre
    noise_rect(d, 60, 200, 144, 144, 6, seed=115)
    d.rounded_rectangle([250, 214, 620, 244], radius=6, fill="#3d1214", outline=RED, width=2)
    d.text((264, 220), "Şifre: Sup3rS3cret!2026", font=font(17, bold=True), fill=RED)

    d.text((60, 390), "Gerçek olay: Meta (Facebook/Instagram), Eylül 2026 — ödül:", font=font(17), fill=DIM)
    d.text((60, 414), "$115.000", font=font(40, bold=True), fill=GREEN)
    d.text((60, 470), "github.com/Rollingzzzzz/heif-heist-lab", font=font(17, bold=True), fill=CYAN)
    d.text((60, 496), "dene:  docker compose up -d --build   →   python exploit/heif_exploit.py",
           font=font(15), fill=DIM)

    return img


# ---------------------------------------------------------------- birleştir
def ease(x):
    return x * x * (3 - 2 * x)


def main():
    scenes = []
    for i in range(8):                                    # giriş
        scenes.append(scene_login(ease(i / 7)))
    for i in range(10):                                   # yükleme
        scenes.append(scene_upload(i / 9))
    for i in range(9):                                    # arka plan
        scenes.append(scene_background(i / 8))
    for i in range(7):                                    # avatar güncellendi
        scenes.append(scene_updated(i / 6))
    for i in range(8):                                    # tıklama + modal
        scenes.append(scene_click(i / 7))
    for i in range(10):                                   # şifre ortaya çıkar
        scenes.append(scene_reveal(i / 9))
    for i in range(10):                                   # kapanış
        scenes.append(scene_outro(min(1.0, i / 7)))

    out_dir = Path(__file__).resolve().parents[1] / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "heif-heist-flow.gif"

    pframes = [f.convert("P", palette=Image.ADAPTIVE, colors=160) for f in scenes]
    pframes[0].save(out, save_all=True, append_images=pframes[1:],
                    duration=150, loop=0, optimize=True)
    print(f"OK: {out}  ({len(pframes)} kare, {out.stat().st_size / 1024:.0f} KB)")

    for idx in (2, 9, 18, 27, 34, 43, 52, len(scenes) - 1):
        scenes[idx].save(out_dir / f"_preview_{idx:02d}.png")


if __name__ == "__main__":
    main()
