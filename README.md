# Seahawks Network Scanner

Un outil de scan réseau développé avec Flask et Python, permettant le scan de ports multiples, le ping de serveurs, et l'envoi de données réseau à une machine distante dans le cadre d'un projet MSPR. Ce projet est composé de deux parties : un client (le scanner) et un serveur (le récepteur).

## Fonctionnalités

### Client (Seahawks Network Scanner)
- **Détection et scan des interfaces réseau actives** :
  - Liste toutes les interfaces réseau avec leur statut (actif/inactif).
  - Scan des ports ouverts sur chaque interface.
- **Informations détaillées du système** :
  - Nom d'hôte.
  - Adresses IP avec notation CIDR.
  - Masques de sous-réseau.
- **Ping serveur** :
  - Test de connectivité avec mesure de latence.
  - Support des formats de sortie en français et en anglais.
- **Interface web responsive** :
  - Visualisation des informations système et des résultats de scan.
  - Configuration de l'URL cible pour l'envoi des données.
  - Minuteur affichant le temps restant avant le prochain envoi automatique.
  - Bouton "Force Send Now" pour envoyer les données immédiatement.
- **Envoi automatique des données** :
  - Envoie les informations système (`system-info`) et les résultats de scan (`scan-results`) à une machine distante toutes les 10 minutes.
  - Stockage persistant de l'URL cible dans un fichier `config.json`.

### Serveur (Receiver)
- **Réception des données** :
  - API Flask simple (`receiver.py`) pour recevoir les données via une requête POST sur `/receive`.
- **Stockage des données** :
  - Enregistrement des données dans une base de données MariaDB (`network_scanner`).
  - Tables pour les informations système (`system_info`, `network_interfaces`) et les résultats de scan (`scan_results`, `open_ports`).

## Prérequis

### Pour le Client
- **Python 3.8 ou supérieur**
- **Nmap (Network Mapper)** pour les scans de ports
- **MariaDB** (optionnel, pour le serveur si vous activez le stockage des données)

#### Installation de Nmap
##### Windows :
1. Téléchargez Nmap depuis [nmap.org](https://nmap.org/download.html)
2. Exécutez l'installateur
3. Ajoutez Nmap au PATH système (par exemple, `C:\Program Files (x86)\Nmap`)

##### Linux :
```bash
sudo apt-get update
sudo apt-get install nmap
```

#### Prérequis supplémentaires pour Linux
```bash
sudo apt install python3.12-venv
```

### Pour le Serveur
- MariaDB installé sur la machine cible.
- Python 3.8 ou supérieur pour exécuter receiver.py.

#### Installation de MariaDB (Serveur)
```bash
sudo apt-get update
sudo apt-get install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
sudo mysql_secure_installation
```

## Installation

### Client (Seahawks Network Scanner)
1. Clonez le dépôt :
```bash
git clone https://github.com/Saint-Pedro/seahawk-network-scanner-II
cd seahawks-network-scanner-II
```

2. Créez un environnement virtuel :
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```
Vérifiez que les bibliothèques requests, schedule, psutil, et python-nmap sont incluses.

### Serveur (Receiver)
1. Le fichier receiver.py se trouve dans le dossier "serveur" du projet.

2. Créez un environnement virtuel (optionnel mais recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# Ou .\venv\Scripts\activate sur Windows
```

3. Créez un fichier requirements.txt pour le serveur :
```
Flask==2.3.3
Werkzeug==2.3.7
flask-cors==4.0.0
mysql-connector-python==9.0.0
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration de la Base de Données (Serveur)

### Étape 1 : Créer la base de données
1. Connectez-vous à MariaDB :
```bash
mysql -u root -p
```

2. Exécutez le script create_database.sql pour créer la base de données et les tables :
```sql
SOURCE /chemin/vers/create_database.sql;
```

Contenu de create_database.sql :
```sql
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
```

3. Créez un utilisateur pour l'application :
```sql
CREATE USER 'toto'@'localhost' IDENTIFIED BY 'toto';
GRANT ALL PRIVILEGES ON network_scanner.* TO 'toto'@'localhost';
FLUSH PRIVILEGES;
```

### Étape 2 : Configurer receiver.py
Mettez à jour les identifiants dans receiver.py :

```python
db_config = {
    'host': 'localhost',
    'database': 'network_scanner',
    'user': 'toto',
    'password': 'toto'
}
```

## Lancement de l'Application

### Serveur (Receiver)
Lancez le serveur sur la machine cible :
```bash
python serveur/receiver.py
```
Le serveur écoute par défaut sur http://<machine-ip>:5001/receive.

### Client (Seahawks Network Scanner)
1. Activez l'environnement virtuel (si ce n'est pas déjà fait) :
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Définissez les variables d'environnement Flask :
```bash
# Windows
set FLASK_APP=app
set FLASK_ENV=development

# Linux/Mac
export FLASK_APP=app
export FLASK_ENV=development
```

3. Lancez l'application :
```bash
flask run
```

4. Accédez à l'application dans votre navigateur : http://127.0.0.1:5000

## Utilisation

### Client (Seahawks Network Scanner)
1. **Informations Système** :
   - Visualisez votre nom d'hôte et toutes vos interfaces réseau.
   - Pour chaque interface, consultez l'adresse IP, le masque de sous-réseau en notation CIDR, et le statut (actif/inactif).

2. **Scanner les Ports Locaux** :
   - Cliquez sur "Start Network Scan" pour scanner les ports de toutes vos interfaces réseau.
   - Les résultats affichent par interface la liste des ports ouverts et leurs services associés.

3. **Ping Serveur** :
   - Entrez une adresse IP dans le champ de saisie.
   - Cliquez sur "Ping Server" pour tester la connectivité et mesurer la latence.
   - Supporte automatiquement les formats de sortie en français et en anglais.

4. **Configurer l'Envoi Automatique** :
   - Allez à la section "Configure Target Server".
   - Entrez l'URL de la machine cible (par exemple, http://<machine-ip>:5001/receive).
   - Cliquez sur "Set Target URL" pour sauvegarder l'adresse.
   - Une fois configurée, les informations système et les résultats de scan seront envoyés automatiquement toutes les 10 minutes.

5. **Minuteur et Envoi Forcé** :
   - Un minuteur affiche le temps restant avant le prochain envoi automatique (10 minutes par défaut).
   - Cliquez sur "Force Send Now" pour envoyer immédiatement les données (system-info et scan-results).

### Serveur (Receiver)
Les données envoyées par le client sont enregistrées dans la base de données MariaDB.
Vérifiez les données stockées avec :
```sql
USE network_scanner;
SELECT * FROM system_info;
SELECT * FROM network_interfaces;
SELECT * FROM scan_results;
SELECT * FROM open_ports;
```

## Notes Techniques

### Client
- Utilise psutil pour une détection précise des interfaces réseau.
- Le scan des ports est réalisé via python-nmap.
- Utilise requests pour envoyer les données à la machine distante.
- La bibliothèque schedule planifie les envois automatiques toutes les 10 minutes.
- Support multi-plateforme (Windows, Linux, macOS).
- Détection intelligente des encodages de sortie pour les commandes système.

### Serveur
- API Flask simple (receiver.py) écoutant sur /receive.
- Utilise mysql-connector-python pour interagir avec MariaDB.
- Gère les requêtes CORS avec flask-cors.
- Stocke les données dans deux ensembles de tables :
  - system_info et network_interfaces pour les informations système.
  - scan_results et open_ports pour les résultats de scan.

## Notes de Sécurité
- Certaines fonctionnalités (comme le scan de ports) peuvent nécessiter des droits administrateurs.
- Cet outil est destiné uniquement à l'administration et aux tests réseau.
- Assurez-vous d'avoir l'autorisation de scanner le réseau/système cible.
- Utilisez de manière responsable et conformément aux politiques de sécurité de votre organisation.
- Pour l'envoi de données, sécurisez la connexion avec HTTPS et ajoutez une authentification si nécessaire.

## Dépannage

### Client
- **Windows** : Si vous rencontrez des problèmes d'encodage, vérifiez que votre terminal supporte l'encodage cp850.
- **Linux** : Assurez-vous que le package python3-venv est installé (sudo apt install python3-venv).
- **Pare-feu** : Les scans de ports peuvent être bloqués par un pare-feu ; vérifiez vos paramètres de sécurité.
- **Envoi automatique** : Si l'envoi échoue, vérifiez que l'URL cible est correcte et que la machine cible est accessible.
- **Minuteur** : Si le minuteur ne fonctionne pas, vérifiez la console JavaScript (F12) pour des erreurs.

### Serveur
- **Erreur de connexion MariaDB** : Vérifiez que MariaDB est en cours d'exécution (sudo systemctl status mariadb) et que les identifiants dans receiver.py sont corrects.
- **Erreur CORS** : Si vous obtenez une erreur NetworkError, assurez-vous que receiver.py est configuré avec flask-cors et que l'origine (http://127.0.0.1:5000 ou l'IP de votre client) est autorisée. Vérifiez également que le port (par défaut 5001) est ouvert.
