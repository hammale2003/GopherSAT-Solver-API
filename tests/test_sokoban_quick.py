"""
Test rapide du Sokoban corrigé
"""
import sys
sys.path.insert(0, '/mnt/user-data/outputs')

from sokoban_solver import SokobanSAT
from sokoban_simulator import SokobanSimulator

GOPHERSAT_PATH = r"C:\Users\hp\Downloads\gophersat\gophersat.exe"

def test_simple():
    print("\n" + "="*60)
    print("TEST RAPIDE - Configuration Simple")
    print("="*60)
    
    # Dans le modèle 1D, il n'y a PAS de murs aux extrémités
    # Les murs (# dans l'image) entourent le terrain mais ne font pas partie du modèle 1D
    initial_state = {"worker": 5, "boxes": [2, 8]}
    goals = [1, 9]  # Goals aux positions 1 et 9
    T = 15
    
    print(f"\nModèle 1D (pas de murs):")
    print(f"Positions: 0 1 2 3 4 5 6 7 8 9 10")
    print(f"État:        . $ @ $ .")
    print(f"Worker: {initial_state['worker']}, Boxes: {initial_state['boxes']}, Goals: {goals}")
    print(f"Note: Toutes les positions 0-10 sont valides")
    
    solver = SokobanSAT(GOPHERSAT_PATH)
    result = solver.solve(initial_state, goals, T=T, num_cells=11)
    
    if "error" in result:
        print(f"\n✗ ERREUR: {result['error']}")
        return False
    
    if result["satisfiable"]:
        print(f"\n✓ SATISFIABLE - Plan trouvé en {len(result['plan'])} étapes")
        
        # Afficher le plan
        print("\nPlan COMPLET:")
        for time, action in result['plan']:
            symbols = {'move_right': '→', 'move_left': '←', 'push_right': '⇒', 'push_left': '⇐'}
            print(f"  t={time:2d}: {symbols.get(action, action)}")
        
        # Simuler
        print("\n--- SIMULATION ---")
        simulator = SokobanSimulator(num_cells=11)
        simulator.set_initial_state(initial_state['worker'], initial_state['boxes'], goals)
        
        # Simulation verbose
        for i, (time, action) in enumerate(result['plan']):
            state_before = simulator.get_state()
            success, message = simulator.execute_action(action)
            
            if not success:
                print(f"\n✗ ÉCHEC à l'étape {i} (t={time})")
                print(f"  Action: {action}")
                print(f"  État avant: worker={state_before['worker']}, boxes={state_before['boxes']}")
                print(f"  Erreur: {message}")
                print(f"\n❌ TEST ÉCHOUÉ")
                return False
        
        # Vérifier le goal
        if simulator.is_goal_reached():
            print(f"\n✓ SIMULATION RÉUSSIE")
            print(f"✓ Objectif atteint!")
            
            final_state = simulator.get_state()
            print(f"\nÉtat final:")
            print(f"  Worker: position {final_state['worker']}")
            print(f"  Boxes: positions {final_state['boxes']}")
            print(f"  Goals: positions {goals}")
            print("\n🎉 SUCCESS! Le plan est valide et atteint l'objectif!")
            return True
        else:
            print(f"\n✓ Simulation terminée MAIS objectif non atteint")
            final_state = simulator.get_state()
            print(f"  Boxes finales: {final_state['boxes']}")
            print(f"  Goals attendus: {goals}")
            return False
    else:
        print(f"\n✗ NON SATISFIABLE avec T={T}")
        return False

if __name__ == "__main__":
    success = test_simple()
    print("\n" + "="*60)
    if success:
        print("✅ TEST PASSÉ - Le solveur fonctionne correctement!")
    else:
        print("❌ TEST ÉCHOUÉ - Il reste des problèmes à corriger")
    print("="*60)