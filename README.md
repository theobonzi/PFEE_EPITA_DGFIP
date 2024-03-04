# PFEE_EPITA_DGFIP

## Installation

### Prérequis

- Python 3.9+
- [Optionnel] Environnement virtuel tel que Conda ou venv

### Étapes d'installation

1. **Clonez le dépôt** :

   ```bash
   git clone [URL_DU_REPO]
   ```

2. **Installez les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

### Utilisation

#### Avec Streamlit (stream.py)

Pour lancer une interface utilisateur interactive avec Streamlit :

```bash
streamlit run stream.py
```

L'interface vous permettra d'effectuer des opérations de prétraitement, d'inférence sur des fichiers ou des documents Excel, et de lancer des benchmarks.

#### Avec run.py

Le script principal run.py peut être utilisé pour effectuer des opérations de prétraitement et d'inférence.

- **Pour réaliser une inférence sur un fichier** :

```bash
python run.py -inference_file <chemin_vers_le_fichier> -ocr <google|trocr|tesseract> [-nb_ocr <nombre>]
```

- **Pour réaliser une inférence à partir d'un fichier Excel** :

```bash
python run.py -inference_excel <chemin_vers_le_fichier_excel> -ocr <google|trocr|tesseract> [-nb_files <nombre>] [-nb_ocr <nombre>]
```

#### Options communes pour l'inférence :

- `-ocr` : Spécifie le moteur OCR à utiliser (`google`, `trocr`, `tesseract`).
- `-nb_ocr` : Définit le nombre d'OCR à traiter.

#### Benchmarks

Pour exécuter des benchmarks et afficher dynamiquement les résultats :

```bash
python3 Benchmark/dash_benchmarks.py
```

Visitez ensuite l'application dans votre navigateur à l'adresse :

```arduino
http://127.0.0.1:8050/
```
