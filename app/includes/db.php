<?php
/**
 * Feysbuk — Veritabanı bağlantısı (MariaDB, docker-compose servis adı: db)
 * Demo basitliği için kimlik bilgileri kodda gömülü; üretimde environment
 * variable kullanılırdı.
 */
$pdo = new PDO(
    'mysql:host=db;dbname=feysbuk;charset=utf8mb4',
    'feysbuk',
    'feysbuk_db_pass',
    [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]
);
