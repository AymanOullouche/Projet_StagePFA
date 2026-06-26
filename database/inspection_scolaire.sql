CREATE DATABASE IF NOT EXISTS inspection_scolaire
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE inspection_scolaire;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL UNIQUE,
  role ENUM('ADMIN', 'INSPECTEUR') NOT NULL DEFAULT 'INSPECTEUR',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etablissements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nom VARCHAR(160) NOT NULL,
  type ENUM('Primaire', 'College', 'Lycee') NOT NULL,
  adresse VARCHAR(255) NOT NULL,
  ville VARCHAR(100) NOT NULL,
  region VARCHAR(140) NOT NULL,
  score INT NOT NULL DEFAULT 70,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inspections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  etablissement_id INT NOT NULL,
  salle VARCHAR(120) NOT NULL,
  statut ENUM('EN_COURS', 'TERMINEE', 'ARCHIVEE') NOT NULL DEFAULT 'EN_COURS',
  date_inspection DATE NOT NULL,
  score_global INT NOT NULL DEFAULT 0,
  anomalies INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_inspections_etablissement
    FOREIGN KEY (etablissement_id) REFERENCES etablissements(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rapports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  inspection_id INT NULL,
  titre VARCHAR(180) NOT NULL,
  etablissement VARCHAR(160) NOT NULL,
  date_generation DATE NOT NULL,
  statut ENUM('Pret', 'Brouillon') NOT NULL DEFAULT 'Brouillon',
  anomalies INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_rapports_inspection
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS session_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  token VARCHAR(128) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_session_tokens_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS anomalies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  inspection_id INT NOT NULL,
  type VARCHAR(120) NOT NULL,
  description TEXT NOT NULL,
  gravite ENUM('MOYENNE', 'ELEVEE', 'CRITIQUE') NOT NULL DEFAULT 'MOYENNE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_anomalies_inspection
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
    ON DELETE CASCADE
);

INSERT INTO users (nom, email, role) VALUES
  ('Admin Systeme', 'admin@inspection.ma', 'ADMIN'),
  ('Inspecteur Principal', 'inspecteur@inspection.ma', 'INSPECTEUR')
ON DUPLICATE KEY UPDATE nom = VALUES(nom), role = VALUES(role);

INSERT INTO etablissements (id, nom, type, adresse, ville, region, score) VALUES
  (1, 'Lycee Ibn Sina', 'Lycee', 'Avenue Al Massira', 'Rabat', 'Rabat-Sale-Kenitra', 82),
  (2, 'College Al Farabi', 'College', 'Quartier administratif', 'Sale', 'Rabat-Sale-Kenitra', 68),
  (3, 'Ecole Al Amal', 'Primaire', 'Route principale', 'Temara', 'Rabat-Sale-Kenitra', 74)
ON DUPLICATE KEY UPDATE
  nom = VALUES(nom),
  type = VALUES(type),
  adresse = VALUES(adresse),
  ville = VALUES(ville),
  region = VALUES(region),
  score = VALUES(score);

INSERT INTO inspections (id, etablissement_id, salle, statut, date_inspection, score_global, anomalies) VALUES
  (101, 1, 'Salle informatique', 'TERMINEE', '2026-06-18', 82, 2),
  (102, 2, 'Laboratoire', 'EN_COURS', '2026-06-22', 68, 5),
  (103, 3, 'Salle standard', 'TERMINEE', '2026-06-10', 74, 3)
ON DUPLICATE KEY UPDATE
  etablissement_id = VALUES(etablissement_id),
  salle = VALUES(salle),
  statut = VALUES(statut),
  date_inspection = VALUES(date_inspection),
  score_global = VALUES(score_global),
  anomalies = VALUES(anomalies);

INSERT INTO rapports (id, inspection_id, titre, etablissement, date_generation, statut, anomalies) VALUES
  (301, 101, 'Rapport inspection - Lycee Ibn Sina', 'Lycee Ibn Sina', '2026-06-18', 'Pret', 2),
  (302, 102, 'Rapport preliminaire - College Al Farabi', 'College Al Farabi', '2026-06-22', 'Brouillon', 5)
ON DUPLICATE KEY UPDATE
  titre = VALUES(titre),
  etablissement = VALUES(etablissement),
  date_generation = VALUES(date_generation),
  statut = VALUES(statut),
  anomalies = VALUES(anomalies);
