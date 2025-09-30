CREATE TABLE `cliente` (
  `id_cliente` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(160) NOT NULL,
  `email` VARCHAR(190) NOT NULL,
  `telefone` VARCHAR(40) DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `uk_cliente_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `url` (
  `id_url` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_cliente` INT UNSIGNED NOT NULL,
  `endereco_url` VARCHAR(255) NOT NULL,
  `ativa` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_url`),
  KEY `idx_url_cliente` (`id_cliente`),
  CONSTRAINT `fk_url_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `relatorio` (
  `id_relatorio` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_url` INT UNSIGNED NOT NULL,
  `gerado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_expiracao` DATE GENERATED ALWAYS AS (DATE(`gerado_em` + INTERVAL 30 DAY)) STORED,
  `resumo` TEXT DEFAULT NULL,
  PRIMARY KEY (`id_relatorio`),
  KEY `idx_relatorio_url` (`id_url`),
  CONSTRAINT `fk_relatorio_url` FOREIGN KEY (`id_url`) REFERENCES `url` (`id_url`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `niveis` (
  `id_nivel` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nome` ENUM('Critico', 'Alto', 'Medio', 'Baixo', 'Informativo') NOT NULL,
  `peso` TINYINT UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`id_nivel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `falhas` (
  `id_falha` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_relatorio` INT UNSIGNED NOT NULL,
  `id_nivel` TINYINT UNSIGNED NOT NULL,
  `titulo` VARCHAR(255) NOT NULL,
  `descricao` TEXT DEFAULT NULL,
  `evidencias` TEXT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_falha`),
  KEY `idx_falhas_relatorio` (`id_relatorio`),
  KEY `idx_falhas_nivel` (`id_nivel`),
  CONSTRAINT `fk_falhas_relatorio` FOREIGN KEY (`id_relatorio`) REFERENCES `relatorio` (`id_relatorio`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_falhas_nivel` FOREIGN KEY (`id_nivel`) REFERENCES `niveis` (`id_nivel`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `sugestao` (
  `id_sugestao` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `id_falha` INT UNSIGNED NOT NULL,
  `texto` TEXT NOT NULL,
  PRIMARY KEY (`id_sugestao`),
  KEY `idx_sugestao_falha` (`id_falha`),
  CONSTRAINT `fk_sugestao_falha` FOREIGN KEY (`id_falha`) REFERENCES `falhas` (`id_falha`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
