<?php
declare(strict_types=1);

session_start();
require_once '/var/www/includes/db.php';

// Zaten giriş yapılmışsa akışa yönlendir
if (isset($_SESSION['user_id'])) {
    header('Location: home.php');
    exit;
}

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $stmt = $pdo->prepare('SELECT id, name, password_hash FROM users WHERE email = ?');
    $stmt->execute([trim((string) ($_POST['email'] ?? ''))]);
    $user = $stmt->fetch();

    if ($user && password_verify((string) ($_POST['password'] ?? ''), $user['password_hash'])) {
        session_regenerate_id(true);
        $_SESSION['user_id'] = (int) $user['id'];
        $_SESSION['name']    = (string) $user['name'];
        header('Location: home.php');
        exit;
    }
    $error = 'E-posta veya şifre hatalı. Tekrar deneyin.';
}
?>
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Feysbuk — Giriş Yap</title>
<link rel="stylesheet" href="style.css">
</head>
<body class="login-body">
  <div class="login-wrap">
    <div class="login-brand">
      <h1 class="logo">feysbuk</h1>
      <p>Feysbuk, tanıdıklarınızla bağlantıda kalmanın kolay yoludur. (demo)</p>
    </div>
    <div class="login-card">
      <?php if ($error): ?><div class="alert"><?= htmlspecialchars($error) ?></div><?php endif; ?>
      <form method="post" action="index.php">
        <input type="email" name="email" placeholder="E-posta" required autofocus
               value="<?= htmlspecialchars((string) ($_POST['email'] ?? '')) ?>">
        <input type="password" name="password" placeholder="Şifre" required>
        <button type="submit" class="btn btn-primary btn-block">Giriş Yap</button>
      </form>
      <hr>
      <p class="hint">Demo hesabı: <code>demo@feysbuk.test</code> / <code>demo1234</code></p>
    </div>
  </div>
  <footer class="login-footer">
    Bu proje bir <strong>güvenlik eğitim laboratuvarıdır</strong>; tüm veriler sahtedir,
    yalnızca yerel Docker ortamında çalıştırılmalıdır.
  </footer>
</body>
</html>
