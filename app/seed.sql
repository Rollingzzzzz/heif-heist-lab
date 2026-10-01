-- Feysbuk demo — tohum verisi (SAHTE verilerdir)
SET NAMES utf8mb4;
USE feysbuk;

CREATE TABLE users (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  email         VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_admin      TINYINT(1) NOT NULL DEFAULT 0,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE posts (
  id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id    INT UNSIGNED NOT NULL,
  body       TEXT NOT NULL,
  attachment VARCHAR(255) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Şifreler (demo):
--   demo@feysbuk.test   -> demo1234
--   ayse@feysbuk.test   -> ayse1234
--   mehmet@feysbuk.test -> mehmet1234
INSERT INTO users (id, name, email, password_hash) VALUES
(1, 'Demo Kullanıcı', 'demo@feysbuk.test',   '$2y$10$TlJntXZDyVHAYRhI//5SIuiaKCgKBQRN5nKSDHCja4xj0M4vWkHCq'),
(2, 'Ayşe Yılmaz',    'ayse@feysbuk.test',   '$2y$10$GtJSz/Q0eGJQ1c617.bykeVDIZl81EY475dZxVAPLLozrS0XyeR4K'),
(3, 'Mehmet Demir',   'mehmet@feysbuk.test', '$2y$10$U5.58g8lC4kNrlwF6U39dukcx2jqY5cuHurs1hPUzHZeQbfA0GxrC');

INSERT INTO posts (user_id, body, attachment) VALUES
(3, 'Kapadokya tatilinden döndum! Balon turu rezervasyon notlarimi ekliyorum, isinize yarar.', 'balon-turu-notlari.txt'),
(2, 'Bu yil okudugum kitaplarin listesi. Sira sizde!', 'kitap-listesi.txt'),
(3, 'Hafta sonu piknik plani hazir, liste ektedir. Gelen catiya yazsin.', 'piknik-listesi.txt');
