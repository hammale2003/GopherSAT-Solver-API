"""
Script de test pour vérifier que les visualisations fonctionnent
"""
import requests
import base64
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

def save_image(base64_data, filename):
    """Sauvegarde une image base64 en fichier PNG"""
    image_data = base64.b64decode(base64_data)
    with open(filename, 'wb') as f:
        f.write(image_data)
    print(f"✓ Image sauvegardée: {filename}")

def test_graph_coloring():
    """Test de coloriage de graphe avec visualisation"""
    print("\n" + "="*60)
    print("TEST: Coloriage de Graphe")
    print("="*60)
    
    data = {
        "V": ["A", "B", "C", "D"],
        "E": [["A", "B"], ["A", "C"], ["B", "C"], ["B", "D"], ["C", "D"]],
        "K": ["r", "v", "b"]
    }
    
    print(f"\nGraphe: V={data['V']}, E={data['E']}, K={data['K']}")
    
    response = requests.post(f"{API_URL}/graph-coloring", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        if result["satisfiable"]:
            print(f"\n✓ SATISFIABLE")
            print(f"Coloriage φ: {result['phi']}")
            print(f"Couleurs utilisées: {result['stats']['colors_used']}")
            
            if result.get("plot"):
                save_image(result["plot"], "graph_coloring_result.png")
            else:
                print("⚠ Pas de visualisation disponible")
        else:
            print(f"\n✗ NON SATISFIABLE: {result['message']}")
    else:
        print(f"\n✗ Erreur HTTP {response.status_code}")
        print(response.text)

def test_sudoku():
    """Test de Sudoku avec visualisation"""
    print("\n" + "="*60)
    print("TEST: Sudoku")
    print("="*60)
    
    data = {
        "grid": [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
    }
    
    print("\nGrille initiale:")
    for row in data["grid"]:
        print("  " + " ".join(str(x) if x != 0 else "." for x in row))
    
    response = requests.post(f"{API_URL}/sudoku", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        if result["satisfiable"]:
            print(f"\n✓ SATISFIABLE")
            print(f"Cases initiales: {result['stats']['filled_cells']}")
            print(f"Cases résolues: {result['stats']['empty_cells']}")
            
            print("\nGrille résolue:")
            for row in result["solution"]:
                print("  " + " ".join(str(x) for x in row))
            
            if result.get("plot"):
                save_image(result["plot"], "sudoku_result.png")
            else:
                print("⚠ Pas de visualisation disponible")
        else:
            print(f"\n✗ NON SATISFIABLE: {result['message']}")
    else:
        print(f"\n✗ Erreur HTTP {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("\n🎨 Test des Visualisations")
    print("="*60)
    
    try:
        test_graph_coloring()
        test_sudoku()
        
        print("\n" + "="*60)
        print("✓ Tests terminés!")
        print("="*60)
        print("\nImages générées:")
        print("  - graph_coloring_result.png")
        print("  - sudoku_result.png")
        print("\nOuvrez ces fichiers pour voir les visualisations!")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERREUR: Impossible de se connecter à l'API")
        print(f"Vérifiez que l'API est lancée sur {API_URL}")
        print("Lancez: python gophersat_api.py")
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()