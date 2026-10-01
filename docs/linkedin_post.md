# LinkedIn Gönderi Taslağı (TR) — HEIF Heist yeniden üretimi

Görsel olarak `docs/screenshots/` içindeki kareleri veya kısa ekran kaydını
kullanın; en vurucu kare: noisy avatar + terminalde çalınan `Sup3rS3cret!2026`.

---

**Kısa süre önce Meta, bir araştırmacıya 115.000 $ ödedi. Hata: tek bir görsel yükleme. 📸**

Eylül'de Hacktron'dan Harsh Jaiswal (@rootxharsh) ve ekibi "HEIF Heist"
araştırmasını duyurdu: libheif görüntü kütüphanesindeki bellek bozulması,
crafted bir HEIC/HEIF fotoğraf yüklenerek Facebook ve Instagram'da **uzaktan
kod çalıştırmaya (RCE)** kadar götürüldü. Meta'nın ödeme gerekçesi tek cümle:
"server-side image conversion sırasında HEIC/HEIF işlemede bellek bozulması;
out-of-bounds read/write'e ve potansiyel RCE'ye yol açar." Aynı ekibin
araştırması OpenAI, Slack, GitHub Enterprise ve Next.js'i de vurdu.

Ben de şunu merak ettim: bu sınıfı kendi mini "sosyal ağ"ımda yeniden üretebilir miyim?

Docker'da minik bir Facebook klonu kurdum. Sunucu tarafı pipeline,
iPhone fotoğrafları gibi HEIC dosyalarını libheif ile işliyor. Ve tıpkı
gerçek sunucular gibi, belleğinde yönetici kimlik bilgilerini taşıyor.

Sonra tek bir crafted HEIC yükledim. Dosya decoder'a "96x96 pikselim var"
diyor ama yalnızca 96 bayt veri taşıyor. Pipeline görsel olduğu gibi
alıyor ve 96x96 = 9216 bayt KOPYALIYOR — uzunluğu kontrol etmeden.
Fazla 9120 bayt nereden mi geliyor? Komşu heap bellekten.

Yani dönen "avatar" aslında sunucunun belleğinin karesi. 🧠

İşte sonuç — avatar piksellerinin arasında:

    Yonetim paneli : https://admin.internal.feysbuk.test
    Sifre          : Sup3rS3cret!2026
    API anahtari   : FK-PROD-9f8a...

Hiçbir hata yok, hiçbir çökme yok. Sadece bir kullanıcı "profil fotoğrafı
yükledi" — ve sunucu belleğini ona PNG/BMP olarak teslim etti. AddressSanitizer
aynı dosyada şu kanıtı basıyor: heap-buffer-overflow READ of size 9216.

Buradan çıkarımlar:

1️⃣ Görüntü işleme = saldırganın uzaktan belleğe dokunması. Native C/C++
   decoder'lar (libheif/libde265 sınıfı) sandbox'sız çalışıyorsa tek bir
   fotoğraf, sunucunun en derin hattına kadar gider.

2️⃣ RCE haberleri "sihir" değildir: out-of-bounds read (bilgi sızıntısı) +
   out-of-bounds write (kontrol ele geçirme) + heap grooming. HEIF Heist bunu
   binlerce yükleme denemesiyle üretimde gösterdi.

3️⃣ Savunma basit: decoder'ı güncel tutun (bu hata 1.18.0'da kapandı),
   görüntü işlemeyi izole edin, pipeline'ı ASAN ile test edin,
   şüpheli formatı startup'ta engelleyin (örn. sharp.block).

Not: Ortam tamamen kendi bilgisayarımdaki izole Docker laboratuvarı; kullandığım
hata halka açık bir n-day (libheif ≤ 1.17.6, GitHub issue #1508). Gerçek hiçbir
sisteme test yapılmadı. Proje + PoC üretici + exploit betiği paylaşımda.

Sizin sunucunuz kaç tane "sadece bir görsel" işliyor? 🤳

#AppSec #CyberSecurity #BugBounty #Docker #ImageSecurity #libheif #RCE

---

## Kısa video senaryosu (60–90 sn, ekran kaydı)

1. **(0–10 sn)** `docker compose up -d --build` → Feysbuk arayüzü. "Mini bir sosyal ağ."
2. **(10–25 sn)** benign.heic yükle → temiz gradyan avatar. "Pipeline normal."
3. **(25–50 sn)** crash.heic yükle → avatar gürültülü. "Bu görüntü sunucunun belleği."
4. **(50–70 sn)** `python exploit/heif_exploit.py` → terminal: çalınan
   `Sup3rS3cret!2026` + ASAN heap-buffer-overflow raporu.
5. **(70–90 sn)** Kod: `memcpy(dst, data.data(), width*height)` — "uzunluk
   kontrolsüz tek satır." Kapanış: "Meta bu sınıfa 115 bin dolar ödedi."

## Etik notlar

- Gerçek sistem/şirket üzerinde test iddiası YOK; tamamen izole lab.
- Olay gerçek (HEIF Heist, Eylül 2026) — kullandığımız zafiyet ise aynı
  sınıftan halka açık bir n-day; bunu açıkça yazın (dürüstlük = güvenilirlik).
- Görüntülerdeki tüm kimlik bilgileri sahtedir.
