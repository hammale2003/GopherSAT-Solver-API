# 🎨 GopherSAT Solver API

API FastAPI complète pour résoudre des problèmes SAT, de coloriage de graphe et de Sudoku avec **visualisations graphiques**.

## 🚀 Installation Rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
python gophersat_api.py
```

L'API sera accessible sur : **http://127.0.0.1:8000**

## 🌐 Interface Web Interactive

Ouvrez dans votre navigateur : **http://127.0.0.1:8000/visualizer**

![Interface](https://img.shields.io/badge/Interface-Web-blue)

## ✅ Tests Réussis

Vos tests montrent que tout fonctionne parfaitement :
- ✅ **Coloriage de graphe** : φ = {'A': 'v', 'B': 'b', 'C': 'r', 'D': 'v'}
- ✅ **Sudoku** : 30 cases initiales → 81 cases résolues
- ✅ **Images générées** : PNG créés avec succès

## 📚 Endpoints Disponibles

### `/graph-coloring` - Coloriage avec Visualisation 🎨

```json
POST /graph-coloring
{
  "V": ["A", "B", "C", "D"],
  "E": [["A", "B"], ["A", "C"], ["B", "C"], ["B", "D"], ["C", "D"]],
  "K": ["r", "v", "b"]
}
```

**Retourne :**
- `phi` : Le coloriage φ : V → K
- `plot` : Image base64 du graphe colorié
- `stats` : Statistiques (variables, clauses, couleurs utilisées)

### `/sudoku` - Résolution avec Visualisation 🧩

```json
POST /sudoku
{
  "grid": [[5,3,0,0,7,0,0,0,0], ...]
}
```

**Retourne :**
- `solution` : Grille 9x9 résolue
- `plot` : Image base64 (avant/après)
- `stats` : Cases initiales/résolues, variables, clauses

### Autres Endpoints

- `POST /solve` - Upload fichier CNF
- `GET /visualizer` - Interface web
- `GET /docs` - Documentation Swagger
- `GET /health` - Vérifier GopherSAT

## 🧪 Scripts de Test

```bash
# Générer les images PNG
python test_visualizations.py

# Tests spécifiques
python test_graph_coloring.py
python test_sudoku.py
```

## 📂 Fichiers

- `gophersat_api.py` - API FastAPI
- `graph_coloring.py` - Module coloriage + visualisation
- `sudoku_solver.py` - Module Sudoku + visualisation  
- `visualizer.html` - Interface web
- `requirements.txt` - Dépendances

## 🎨 Visualisations

### Coloriage de Graphe
- Graphe avec **NetworkX**
- Couleurs : r→rouge, v→vert, b→bleu
- Layout spring automatique
- Légende des couleurs

### Sudoku
- **Grilles côte à côte** (initial vs résolu)
- Cases initiales : noir/fond bleu
- Cases calculées : bleu
- Sous-grilles 3x3 délimitées

## 🛠️ Configuration

Modifiez le chemin GopherSAT dans `gophersat_api.py` :
```python
GOPHERSAT_PATH = r"C:\Users\hp\Downloads\gophersat\gophersat.exe"
```

## 🚀 Utilisation

### Via l'interface web
1. Lancez : `python gophersat_api.py`
2. Ouvrez : http://127.0.0.1:8000/visualizer
3. Testez avec les exemples pré-remplis !

### Via Python
```python
import requests

response = requests.post("http://127.0.0.1:8000/graph-coloring", json={
    "V": ["A", "B", "C"],
    "E": [["A", "B"]],
    "K": ["r", "v"]
})
print(response.json()['phi'])  # Coloriage
```

## 📊 Résultats de vos Tests

```
✅ Coloriage : φ = {'A': 'v', 'B': 'b', 'C': 'r', 'D': 'v'}
   - 4 sommets, 5 arêtes
   - 3 couleurs utilisées
   - 12 variables SAT, 31 clauses

✅ Sudoku : Résolu en 51 cases
   - 30 cases initiales
   - 729 variables SAT
   - 11,988 clauses
```

---

**Tout fonctionne ! 🎉 Profitez de l'interface web sur http://127.0.0.1:8000/visualizer**
