-- Créer la base de données
CREATE DATABASE IF NOT EXISTS network_scanner;
USE network_scanner;

-- Table pour les informations système
CREATE TABLE system_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les interfaces réseau (liée à system_info)
CREATE TABLE network_interfaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_info_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(10) NOT NULL, -- up/down
    address_type VARCHAR(10), -- IPv4/IPv6
    address VARCHAR(45), -- Supporte IPv4 et IPv6
    cidr VARCHAR(45), -- Notation CIDR (optionnel)
    netmask VARCHAR(45), -- Netmask (optionnel)
    FOREIGN KEY (system_info_id) REFERENCES system_info(id) ON DELETE CASCADE
);

-- Table pour les résultats de scan
CREATE TABLE scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interface_name VARCHAR(255) NOT NULL,
    ip VARCHAR(45) NOT NULL,
    hostname VARCHAR(255),
    status VARCHAR(10) NOT NULL, -- up/down
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour les ports ouverts (liée à scan_results)
CREATE TABLE open_ports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_result_id INT NOT NULL,
    port INT NOT NULL,
    service VARCHAR(100),
    FOREIGN KEY (scan_result_id) REFERENCES scan_results(id) ON DELETE CASCADE
);