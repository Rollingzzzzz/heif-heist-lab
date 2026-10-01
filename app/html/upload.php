<?php
/**
 * upload.php — Feysbuk profil fotoğrafı yükleme (HEIC pipeline)
 * ---------------------------------------------------------------------------
 * iPhone fotoğrafları gibi HEIC/HEIF dosyalarını kabul eder ve SUNUCU
 * TARAFINDA dönüştürür (heifconv → BMP avatar) — gerçek sosyal ağların
 * "yükle → sunucuda işle" akışının aynısı.
 *
 * Dönüştürücü, libheif 1.17.6'ya bağlıdır (CVE-2025-46087 yaşar) ve — tıpkı
 * gerçek sunucular gibi — belleğinde gizli yönetici verisi taşır
 * (--secret-file). Zafiyetli decoder, crafted bir görüntüde komşu heap'i
 * çıktı avatara KOPYALAR (heap disclosure = "heist").
 */

declare(strict_types=1);

session_start();
require_once '/var/www/includes/db.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

$uid   = (int) $_SESSION['user_id'];
$avDir = '/var/www/uploads/avatars';
if (!is_dir($avDir)) {
    mkdir($avDir, 0777, true);
}

$message = '';
$ok = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['photo'])) {
    $name = (string) $_FILES['photo']['name'];
    $ext  = strtolower(pathinfo($name, PATHINFO_EXTENSION));
    $tmp  = (string) $_FILES['photo']['tmp_name'];
    $size = (int) $_FILES['photo']['size'];

    if (!in_array($ext, ['heic', 'heif'], true)) {
        $message = 'Sadece .heic / .heif kabul edilir (iPhone fotoğrafı gibi).';
    } elseif ($size <= 0 || $size > 8 * 1024 * 1024) {
        $message = 'Dosya boş veya 8 MB sınırını aşıyor.';
    } elseif (!is_uploaded_file($tmp)) {
        $message = 'Yükleme doğrulanamadı.';
    } else {
        $in  = $avDir . '/original_' . $uid . '.' . $ext;
        $out = $avDir . '/avatar_' . $uid . '.bmp';
        move_uploaded_file($tmp, $in);

        // Sunucu tarafı dönüştürme — gerçek pipeline gibi bellekte gizli
        // yönetici verisi taşır (HEIF Heist senaryosunun "in-memory data"sı).
        $cmd = sprintf(
            'heifconv %s %s --secret-file /var/www/secret/admin_credentials.txt 2>&1',
            escapeshellarg($in),
            escapeshellarg($out)
        );
        $pipelineOut = shell_exec($cmd);
        $code = 0;
        // shell_exec çıkış kodunu vermez; proc_open ile almak yerine dosya
        // varlığına bakılır (demo basitliği).
        $ok = is_file($out) && filesize($out) > 54;

        $log = sprintf(
            "[%s] user=%d file=%s size=%d exit=%s\n  %s\n",
            date('Y-m-d H:i:s'),
            $uid,
            basename($name),
            $size,
            $ok ? '0 (dönüştürüldü)' : 'HATA',
            trim((string) $pipelineOut)
        );
        file_put_contents($avDir . '/heif_pipeline.log', $log, FILE_APPEND);

        $message = $ok
            ? 'Profil fotoğrafın dönüştürüldü ve yüklendi.'
            : 'Pipeline dosyayı işleyemedi (log kayıtlarına bak).';
    }
}

header('Location: home.php?upload=' . ($ok ? 'ok' : 'fail') . '&msg=' . urlencode($message));
exit;
