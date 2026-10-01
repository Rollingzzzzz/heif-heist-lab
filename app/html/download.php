<?php
/**
 * download.php — yüklenen ekleri ve dönüştürülen avatarları sunar.
 * Yol güvenliği: kullanıcı girdisi HER ZAMAN uploads köküne bağlanır ve
 * symlink'ler dahil çözülen gerçek yol (realpath) beyaz listeye göre
 * doğrulanır. /var/www/secret tamamen erişilemez.
 */

declare(strict_types=1);

session_start();
require_once '/var/www/includes/db.php';

if (!isset($_SESSION['user_id'])) {
    http_response_code(403);
    die('403 — Oturum açmanız gerekir.');
}

$f = $_GET['f'] ?? '';
if ($f === '') {
    http_response_code(400);
    die('400 — f parametresi gerekli.');
}

$uploadsRoot = '/var/www/uploads/';

$full = $uploadsRoot . $f;
$real = realpath($full);

if ($real === false || !str_starts_with($real, $uploadsRoot) || !is_file($real)) {
    http_response_code(404);
    die('404 — Dosya bulunamadı.');
}

$mime = (new finfo(FILEINFO_MIME_TYPE))->file($real) ?: 'application/octet-stream';
if (str_starts_with($mime, 'text/')) {
    $mime .= '; charset=utf-8';
}
header('Content-Type: ' . $mime);
header('Content-Length: ' . (string) filesize($real));
readfile($real);
