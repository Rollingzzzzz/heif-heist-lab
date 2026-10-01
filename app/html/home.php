<?php
declare(strict_types=1);

session_start();
require_once '/var/www/includes/db.php';

if (!isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

// Basit paylaş kutusu: metin gönderisi ekle
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = trim((string) ($_POST['body'] ?? ''));
    if ($body !== '') {
        $stmt = $pdo->prepare('INSERT INTO posts (user_id, body) VALUES (?, ?)');
        $stmt->execute([$_SESSION['user_id'], $body]);
        header('Location: home.php');
        exit;
    }
}

$posts = $pdo->query(
    'SELECT p.id, p.body, p.attachment, p.created_at, u.name
     FROM posts p JOIN users u ON u.id = p.user_id
     ORDER BY p.id DESC LIMIT 30'
)->fetchAll();

// Profil fotoğrafı (pipeline çıktısı) varsa göster
$uid        = (int) $_SESSION['user_id'];
$avatarFile = '/var/www/uploads/avatars/avatar_' . $uid . '.bmp';
$hasAvatar  = is_file($avatarFile);
$avatarUrl  = 'download.php?f=avatars/avatar_' . $uid . '.bmp';
$uploadMsg  = isset($_GET['upload']) ? [
    'type'    => $_GET['upload'],
    'message' => (string) ($_GET['msg'] ?? ''),
] : null;
?>
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feysbuk — Haber Akışı</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="topbar">
  <div class="topbar-inner">
    <a class="logo" href="home.php">feysbuk</a>
    <nav>
      <?php if ($hasAvatar): ?>
        <img class="topbar-avatar" src="<?= htmlspecialchars($avatarUrl) ?>" alt="avatar">
      <?php endif; ?>
      <span class="user-badge"><?= htmlspecialchars($_SESSION['name']) ?></span>
      <a class="btn btn-light" href="logout.php">Çıkış Yap</a>
    </nav>
  </div>
</header>

<main class="layout">
  <section class="feed">
    <?php if ($uploadMsg): ?>
      <div class="alert <?= $uploadMsg['type'] === 'ok' ? 'alert-ok' : '' ?>">
        <?= htmlspecialchars($uploadMsg['message']) ?>
      </div>
    <?php endif; ?>

    <div class="card composer">
      <form method="post" action="home.php">
        <textarea name="body" rows="2" placeholder="Ne düşünüyorsun, <?= htmlspecialchars($_SESSION['name']) ?>?"></textarea>
        <div class="composer-actions">
          <button type="submit" class="btn btn-primary">Paylaş</button>
        </div>
      </form>
    </div>

    <div class="card composer">
      <h3>Profil Fotoğrafı (HEIC)</h3>
      <?php if ($hasAvatar): ?>
        <img class="avatar-preview" src="<?= htmlspecialchars($avatarUrl . '&t=' . filemtime($avatarFile)) ?>" alt="Profil fotoğrafı">
      <?php endif; ?>
      <form method="post" action="upload.php" enctype="multipart/form-data">
        <input type="file" name="photo" accept=".heic,.heif,image/heic,image/heif" required>
        <div class="composer-actions">
          <button type="submit" class="btn btn-primary">Yükle ve Dönüştür</button>
        </div>
      </form>
      <p class="muted">Yüklediğin dosya sunucuda <code>heifconv</code> pipeline'ı ile işlenir
      (iPhone fotoğrafları gibi HEIC/HEIF dosyaları sunucuda dönüştürülür).</p>
    </div>

    <?php foreach ($posts as $p): ?>
      <article class="card post">
        <div class="post-head">
          <span class="avatar"><?= htmlspecialchars(mb_substr($p['name'], 0, 1)) ?></span>
          <div>
            <strong><?= htmlspecialchars($p['name']) ?></strong>
            <small><?= htmlspecialchars((string) $p['created_at']) ?></small>
          </div>
        </div>
        <p class="post-body"><?= nl2br(htmlspecialchars($p['body'])) ?></p>
        <?php if (!empty($p['attachment'])): ?>
          <a class="attachment" href="download.php?f=<?= urlencode((string) $p['attachment']) ?>">📎 Ek: <?= htmlspecialchars((string) $p['attachment']) ?></a>
        <?php endif; ?>
      </article>
    <?php endforeach; ?>
  </section>

  <aside class="sidebar">
    <div class="card">
      <h3>Sunucudaki Ekler</h3>
      <p class="muted">Paylaşılan ekler <code>/var/www/uploads</code> altında tutulur ve
      <code>download.php</code> üzerinden sunulur.</p>
      <ul class="linklist">
        <li><a href="download.php?f=balon-turu-notlari.txt">📎 balon-turu-notlari.txt</a></li>
        <li><a href="download.php?f=kitap-listesi.txt">📎 kitap-listesi.txt</a></li>
        <li><a href="download.php?f=piknik-listesi.txt">📎 piknik-listesi.txt</a></li>
        <li><a href="download.php?f=avatars/heif_pipeline.log">📜 heif_pipeline.log</a></li>
      </ul>
    </div>
    <div class="card demo-note">
      <h3>Bu bir demo</h3>
      <p class="muted">Feysbuk, kasıtlı olarak zafiyet barındıran bir eğitim
      laboratuvarıdır. Gerçek bir sosyal ağ değildir.</p>
    </div>
  </aside>
</main>
</body>
</html>
