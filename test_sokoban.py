"""
Script de test pour le Sokorridor
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

def test_sokoban_simple():
    """Test avec un Sokorridor simple"""
    print("\n" + "="*60)
    print("TEST: Sokorridor Simple")
    print("="*60)
    
    # État initial: #. $   @  $.#
    # Positions: 0  1  2  3  4  5  6  7  8  9  10
    # Worker en 6, boxes en 2 et 9, goals en 1 et 10
    
    data = {
        "initial_state": {
            "worker": 6,
            "boxes": [2, 9]
        },
        "goals": [1, 10],
        "T": 15,
        "num_cells": 11
    }
    
    print("\nConfiguration:")
    print(f"  État initial: #. $   @  $.#")
    print(f"  Worker: position {data['initial_state']['worker']}")
    print(f"  Caisses: positions {data['initial_state']['boxes']}")
    print(f"  Objectifs: positions {data['goals']}")
    print(f"  Horizon: T={data['T']}")
    
    response = requests.post(f"{API_URL}/sokoban", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        if result["satisfiable"]:
            print(f"\n✓ SATISFIABLE")
            print(f"Plan trouvé en {result['stats']['plan_length']} étapes:")
            
            for time, action in result['plan']:
                action_names = {
                    'move_right': '→',
                    'move_left': '←',
                    'push_right': '⇒',
                    'push_left': '⇐'
                }
                print(f"  t={time:2d}: {action_names.get(action, action)}")
            
            print(f"\nStatistiques:")
            print(f"  - Variables SAT: {result['stats']['nb_variables']}")
            print(f"  - Clauses SAT: {result['stats']['nb_clauses']}")
            print(f"  - Longueur du plan: {result['stats']['plan_length']}")
            
            if result.get('simulation'):
                print(f"\nSimulation:")
                print(f"  - {result['simulation']['message']}")
                print(f"  - Objectif atteint: {result['simulation']['goal_reached']}")
            
            if result.get('visualizations'):
                print(f"\nVisualizations: {len(result['visualizations'])} images générées")
                
                # Sauvegarder quelques images clés
                vis = result['visualizations']
                save_image(vis[0], "sokoban_step_0_initial.png")
                if len(vis) > 1:
                    save_image(vis[len(vis)//2], f"sokoban_step_{len(vis)//2}_middle.png")
                save_image(vis[-1], f"sokoban_step_{len(vis)-1}_final.png")
            
            if result.get('animated_gif'):
                print(f"\n✓ GIF animé généré")
                save_image(result['animated_gif'], "sokoban_animation.gif")
                print("  → sokoban_animation.gif")
        else:
            print(f"\n✗ NON SATISFIABLE")
            print(f"Message: {result['message']}")
            print(f"Essayez d'augmenter T (actuellement {result['stats']['horizon']})")
    else:
        print(f"\n✗ Erreur HTTP {response.status_code}")
        print(response.text)

def test_sokoban_harder():
    """Test avec un Sokorridor plus difficile"""
    print("\n" + "="*60)
    print("TEST: Sokorridor Plus Difficile")
    print("="*60)
    
    # État initial: #. $$ @    $.#
    # Plus de caisses, configuration plus complexe
    
    data = {
        "initial_state": {
            "worker": 5,
            "boxes": [2, 3, 9]
        },
        "goals": [1, 8, 10],
        "T": 25,  # Horizon plus grand
        "num_cells": 11
    }
    
    print("\nConfiguration:")
    print(f"  État initial: #. $$ @    $.#")
    print(f"  Worker: position {data['initial_state']['worker']}")
    print(f"  Caisses: positions {data['initial_state']['boxes']}")
    print(f"  Objectifs: positions {data['goals']}")
    print(f"  Horizon: T={data['T']}")
    
    response = requests.post(f"{API_URL}/sokoban", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        if result["satisfiable"]:
            print(f"\n✓ SATISFIABLE")
            print(f"Plan trouvé en {result['stats']['plan_length']} étapes")
            
            if result.get('simulation'):
                print(f"Simulation: {result['simulation']['message']}")
        else:
            print(f"\n✗ NON SATISFIABLE avec T={result['stats']['horizon']}")
            print(f"Conseil: augmentez T et réessayez")
    else:
        print(f"\n✗ Erreur HTTP {response.status_code}")
        print(response.text)

def test_sokoban_impossible():
    """Test avec une configuration impossible"""
    print("\n" + "="*60)
    print("TEST: Configuration Impossible")
    print("="*60)
    
    # Configuration impossible: caisses coincées
    data = {
        "initial_state": {
            "worker": 5,
            "boxes": [1, 10]  # Caisses déjà contre les murs
        },
        "goals": [2, 9],  # Impossible de les déplacer
        "T": 10,
        "num_cells": 11
    }
    
    print("\nConfiguration (impossible):")
    print(f"  Worker: position {data['initial_state']['worker']}")
    print(f"  Caisses: positions {data['initial_state']['boxes']} (contre les murs)")
    print(f"  Objectifs: positions {data['goals']}")
    
    response = requests.post(f"{API_URL}/sokoban", json=data)
    
    if response.status_code == 200:
        result = response.json()
        
        if not result["satisfiable"]:
            print(f"\n✓ Correctement détecté comme IMPOSSIBLE")
            print(f"Message: {result['message']}")
        else:
            print(f"\n⚠ Attention: un plan a été trouvé pour une config censée être impossible!")
    else:
        print(f"\n✗ Erreur HTTP {response.status_code}")

if __name__ == "__main__":
    print("\n🎮 Tests du Sokorridor (Planification SAT)\n")
    
    try:
        test_sokoban_simple()
        test_sokoban_harder()
        test_sokoban_impossible()
        
        print("\n" + "="*60)
        print("✓ Tests terminés!")
        print("="*60)
        print("\nImages générées:")
        print("  - sokoban_step_0_initial.png (état initial)")
        print("  - sokoban_step_*_middle.png (étape intermédiaire)")
        print("  - sokoban_step_*_final.png (état final)")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERREUR: Impossible de se connecter à l'API")
        print(f"Vérifiez que l'API est lancée sur {API_URL}")
        print("Lancez: python gophersat_api.py")
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()