/**
 * heifconv.c — Feysbuk "sunucu tarafı görüntü dönüştürme pipeline"ı (demo)
 * ---------------------------------------------------------------------------
 * Gerçek sosyal ağlar gibi yüklenen HEIC/HEIF dosyasını sunucu tarafında
 * dönüştürür (burada: 8-bit gri → 24-bit BMP avatar).
 *
 * libheif 1.17.6'ya bağlanır — CVE-2025-46087 (issue #1508, 1.18.0'da düzeltildi)
 * bu sürümde YAŞAR: decode sırasında 96 baytlık vektörden 9216 bayt okunur
 * (uncompressed_image.cc:756, sınır kontrolsüz memcpy). Kopyalanan veri
 * çıktı görüntüsüne yazıldığı için komşu heap içeriği AVATARA SIZAR.
 *
 * [--secret-file <dosya>] verildiyse, çözümlemeden ÖNCE dosyanın içeriği
 * heap'e püskürtülür (heap grooming) — gerçek sunucuların belleğinde yönetici
 * anahtarları/oturum verisi taşıdığını modeller. Crafted görüntü bu belleği
 * "çalar" (HEIF Heist'teki heap-disclosure primitive'i).
 *
 * Kullanım:
 *   heifconv <girdi.heic> <çıktı.bmp> [--secret-file /var/www/secret/...]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libheif/heif.h>

#define PRIME_BLOCK_SIZE (120u * 1024u)   /* mmap esiginin (128K) altinda -> sbrk heap'i */

/**
 * Heap grooming - deterministik "unsorted bin" yontemi:
 *  1) mmap esigi altinda BUYUK bir blok alinir ve tamami gizli icerikle dolar.
 *  2) free() ile unsorted bin'e birakilir.
 *  3) Sonraki tum kucuk tahsisatlar (libheif parse + 96 B'lik item-data
 *     vektoru DAHIL) bu bloktan BASTAN ITIBAREN sirayla oyulur ("last
 *     remainder" davranisi). Vektor blokun icinde bir yerde yasalar ve
 *     YUKARISI hala gizli icerikle doludur -> 9216 B'lik tasma kacinilmaz
 *     olarak sizintiyi yakalar.
 */
static void *g_pad_keep_alive;   /* blokun ustu dolu kalsin diye bilincli sizinti */

static void groom_heap_with(const unsigned char *secret, size_t secret_len)
{
    unsigned char *block = malloc(PRIME_BLOCK_SIZE);
    if (!block) return;
    if (getenv("HEIFCONV_DEBUG")) fprintf(stderr, "[dbg] block=%p\n", (void*)block);

    /* Blokun uzerine kalici bir pad koy: aksi halde free() tepedeki chunk'i
       top ile birlestirip systrim OS'a geri verir -> sifir sayfalar. */
    g_pad_keep_alive = malloc(PRIME_BLOCK_SIZE);

    const char tag[6] = { 'H', 'E', 'I', 'S', 'T', '!' };
    for (unsigned int k = 0; k < PRIME_BLOCK_SIZE; k++) {
        block[k] = (k % 96 < 6) ? (unsigned char) tag[k % 96]
                                : secret[k % secret_len];
    }

    free(block);   /* unsorted bin -> sonraki kucuk tahsisatlar buradan oyulur */
}

static void write_bmp24_gray(const char *path, const unsigned char *gray,
                             int width, int height, int stride)
{
    int row_bytes = width * 3;          /* 96*3 = 288, 4 bayta zaten hizalı */
    unsigned int data_size = (unsigned int)(row_bytes * height);
    unsigned int file_size = 54 + data_size;

    FILE *f = fopen(path, "wb");
    if (!f) { perror("fopen output"); exit(4); }

    unsigned char hdr[54] = {0};
    hdr[0] = 'B'; hdr[1] = 'M';
    *(unsigned int *)&hdr[2]  = file_size;
    *(unsigned int *)&hdr[10] = 54;
    *(unsigned int *)&hdr[14] = 40;          /* BITMAPINFOHEADER */
    *(int *)&hdr[18] = width;
    *(int *)&hdr[22] = height;               /* alt-tan yukarı */
    *(unsigned short *)&hdr[26] = 1;
    *(unsigned short *)&hdr[28] = 24;
    *(unsigned int *)&hdr[34] = data_size;
    *(unsigned int *)&hdr[38] = 2835;
    *(unsigned int *)&hdr[42] = 2835;
    fwrite(hdr, 1, 54, f);

    unsigned char *row = malloc((size_t)row_bytes);
    for (int y = height - 1; y >= 0; y--) {
        const unsigned char *src = gray + (size_t)y * stride;
        for (int x = 0; x < width; x++) {
            row[x * 3 + 0] = src[x];
            row[x * 3 + 1] = src[x];
            row[x * 3 + 2] = src[x];
        }
        fwrite(row, 1, (size_t)row_bytes, f);
    }
    free(row);
    fclose(f);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "kullanım: %s <girdi.heic> <çıktı.bmp> [--secret-file <dosya>]\n", argv[0]);
        return 1;
    }
    const char *in_path  = argv[1];
    const char *out_path = argv[2];
    const char *secret_path = NULL;
    for (int i = 3; i < argc - 1; i++) {
        if (strcmp(argv[i], "--secret-file") == 0) secret_path = argv[i + 1];
    }

    if (secret_path) {
        FILE *sf = fopen(secret_path, "rb");
        if (sf) {
            static unsigned char secret[16384];
            size_t n = fread(secret, 1, sizeof(secret), sf);
            fclose(sf);
            if (n > 32) {
                groom_heap_with(secret, n);
            }
        }
    }

    /* --- girdi dosyasını belleğe oku --- */
    FILE *f = fopen(in_path, "rb");
    if (!f) { perror("fopen input"); return 2; }
    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *file_mem = malloc((size_t)fsize);
    if (fread(file_mem, 1, (size_t)fsize, f) != (size_t)fsize) { fclose(f); return 2; }
    fclose(f);

    /* --- libheif pipeline (sunucudaki gerçek dönüştürme adımı gibi) --- */
    struct heif_error err;
    struct heif_context *ctx = heif_context_alloc();
    err = heif_context_read_from_memory(ctx, file_mem, (size_t)fsize, NULL);
    if (err.code) {
        fprintf(stderr, "parse hatası: %s (%s)\n", err.message);
        return 3;
    }

    struct heif_image_handle *handle = NULL;
    err = heif_context_get_primary_image_handle(ctx, &handle);
    if (err.code) {
        fprintf(stderr, "handle hatası: %s (%s)\n", err.message);
        return 3;
    }

    struct heif_image *img = NULL;
    err = heif_decode_image(handle, &img,
                            heif_colorspace_monochrome,
                            heif_chroma_monochrome, NULL);
    if (err.code) {
        fprintf(stderr, "decode hatası: %s (%s)\n", err.message);
        return 3;
    }

    int w = heif_image_get_width(img, heif_channel_Y);
    int h = heif_image_get_height(img, heif_channel_Y);
    int stride = 0;
    const uint8_t *plane = heif_image_get_plane_readonly(img, heif_channel_Y, &stride);
    if (!plane) { fprintf(stderr, "plane yok\n"); return 3; }

    write_bmp24_gray(out_path, plane, w, h, stride);

    fprintf(stdout, "dönüştürüldü: %s → %s (%dx%d gri, girdi %ld bayt)\n",
            in_path, out_path, w, h, fsize);

    if (getenv("HEIFCONV_DEBUG")) {
        fprintf(stderr, "[dbg] dst-plane=%p ilk-bayt=%02x\n", (const void*)plane, plane[0]);
        fprintf(stderr, "[dbg] plane+96..: %02x %02x %02x %02x %02x %02x %02x %02x\n",
                plane[96], plane[97], plane[98], plane[99],
                plane[100], plane[101], plane[102], plane[103]);
    }
    heif_image_release(img);
    heif_image_handle_release(handle);
    heif_context_free(ctx);
    free(file_mem);
    return 0;
}
