# Seahawks Network Scanner

Un outil de scan réseau développé avec Flask et Python, permettant le scan de ports multiples et le ping de serveurs dans le cadre d'un projet MSPR.

## Fonctionnalités

- Détection et scan de toutes les interfaces réseau actives
- Scan des ports ouverts sur chaque interface
- Affichage des informations détaillées du système :
  - Nom d'hôte
  - Liste des interfaces réseau avec leurs statuts (actif/inactif)
  - Adresses IP avec notation CIDR
  - Masques de sous-réseau
- Ping serveur avec mesure de latence
- Interface web responsive

## Prérequis

- Python 3.8 ou supérieur
- Nmap (Network Mapper)

### Installation de Nmap

#### Windows :
1. Téléchargez Nmap depuis [nmap.org](https://nmap.org/download.html)
2. Exécutez l'installateur
3. Ajoutez Nmap au PATH système

#### Linux :
```bash
sudo apt-get update
sudo apt-get install nmap
```
### Prérequis supplémentaires pour Linux
```bash
sudo apt install python3.12-venv
```

## Installation

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

## Lancement de l'Application

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

4. Accédez à l'application dans votre navigateur : `http://127.0.0.1:5000`

## Utilisation

1. Informations Système :
   - Visualisez votre nom d'hôte et toutes vos interfaces réseau
   - Pour chaque interface, vous pouvez voir l'adresse IP, le masque de sous-réseau en notation CIDR, et le statut (actif/inactif)

2. Scanner les Ports Locaux :
   - Cliquez sur "Start Network Scan" pour scanner les ports de toutes vos interfaces réseau
   - Les résultats sont affichés par interface, avec la liste des ports ouverts et leurs services associés

3. Ping Serveur :
   - Entrez une adresse IP dans le champ de saisie
   - Cliquez sur "Ping Server" pour tester la connectivité et mesurer la latence
   - Supporte automatiquement les formats de sortie en français et en anglais

## Notes Techniques

- L'application utilise `psutil` pour une détection précise des interfaces réseau
- Le scan des ports est réalisé via `python-nmap`
- Support multi-plateforme (Windows, Linux, macOS)
- Détection intelligente des encodages de sortie pour les commandes système

## Notes de Sécurité

- Certaines fonctionnalités (comme le scan de ports) peuvent nécessiter des droits administrateur
- Cet outil est destiné uniquement à l'administration et aux tests réseau
- Assurez-vous d'avoir l'autorisation de scanner le réseau/système cible
- Utilisez de manière responsable et conformément aux politiques de sécurité de votre organisation

## Dépannage

- Sur Windows, si vous rencontrez des problèmes d'encodage, vérifiez que votre terminal supporte l'encodage cp850
- Sur Linux, assurez-vous que le package python3-venv est installé (`sudo apt install python3-venv`)
- Les pare-feu peuvent bloquer les scans de ports - vérifiez vos paramètres de sécurité
