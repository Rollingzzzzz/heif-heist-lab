# Feysbuk demo — 2004 Facebook'ın LAMP tarzı: Apache + PHP + (harici) MariaDB
FROM php:8.2-apache

# MariaDB bağlantısı için PDO MySQL sürücüsü
RUN docker-php-ext-install pdo_mysql

# ---------------------------------------------------------------------------
# HEIF laboratuvarı — HEIF Heist / CVE-2025-46087 yeniden üretimi
# Savunmasız libheif 1.17.6 (1.18.0'da düzeltildi; issue strukturag/libheif#1508)
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch v1.17.6 \
        https://github.com/strukturag/libheif.git /tmp/libheif

# 1) Düz derleme — "üretim" pipeline'ı: taşma CANLI çalışır, heap çıktıya sızar
RUN cmake -S /tmp/libheif -B /tmp/bh-plain -DCMAKE_BUILD_TYPE=Release \
        -DWITH_UNCOMPRESSED_CODEC=ON \
        -DWITH_EXAMPLES=OFF -DBUILD_TESTING=OFF \
    && cmake --build /tmp/bh-plain -j"$(nproc)" \
    && cmake --install /tmp/bh-plain \
    && ldconfig

# 2) ASAN derlemesi — adli kanıt: taşmayı raporlar (heap-buffer-overflow READ)
RUN cmake -S /tmp/libheif -B /tmp/bh-asan -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DCMAKE_C_FLAGS="-fsanitize=address -g -O1" \
        -DCMAKE_CXX_FLAGS="-fsanitize=address -g -O1" \
        -DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address" \
        -DCMAKE_SHARED_LINKER_FLAGS="-fsanitize=address" \
        -DCMAKE_INSTALL_PREFIX=/opt/heif-asan \
        -DWITH_UNCOMPRESSED_CODEC=ON \
        -DWITH_EXAMPLES=OFF -DBUILD_TESTING=OFF \
    && cmake --build /tmp/bh-asan -j"$(nproc)" \
    && cmake --install /tmp/bh-asan

# Sunucu tarafı dönüştürücü (pipeline ikili dosyası)
COPY heiflab/heifconv.c /usr/local/src/heifconv.c
RUN gcc -O2 -o /usr/local/bin/heifconv /usr/local/src/heifconv.c \
        -I/usr/local/include -L/usr/local/lib -lheif -Wl,-rpath,/usr/local/lib \
    && gcc -O1 -g -fsanitize=address -o /usr/local/bin/heifconv-asan \
        /usr/local/src/heifconv.c \
        -I/opt/heif-asan/include -L/opt/heif-asan/lib -lheif \
        -Wl,-rpath,/opt/heif-asan/lib

# Not:
#   - /var/www/html        → docroot (compose ile ./app/html mount edilir)
#   - /var/www/includes    → docroot dışı uygulama kodu (./app/includes)
#   - /var/www/secret      → docroot dışı KORUNAN bölge (./secret)
#   - /var/www/uploads     → meşru ekler + avatarlar (./uploads)
# Kod bind-mount olduğu için FIX yamaları rebuild gerektirmez;
# yalnızca libheif/heifconv derlemesi image'a gömülüdür.
