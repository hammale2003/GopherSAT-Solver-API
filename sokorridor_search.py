"""
Sokorridor Solver - Recherche non informée (BFS, IDDFS)
Séance 3 - Exemple 2
"""
from typing import List, Tuple, Optional, Set
from collections import deque


class SokorridorState:
    """État du Sokorridor"""
    
    def __init__(self, worker: int, boxes: List[int], num_cells: int = 11):
        self.worker = worker
        self.boxes = tuple(sorted(boxes))  # Tuple pour hachage
        self.num_cells = num_cells
    
    def __eq__(self, other):
        return self.worker == other.worker and self.boxes == other.boxes
    
    def __hash__(self):
        return hash((self.worker, self.boxes))
    
    def __repr__(self):
        return f"State(w={self.worker}, b={list(self.boxes)})"
    
    def to_string(self) -> str:
        """Représentation visuelle"""
        chars = ['.'] * self.num_cells
        chars[0] = '#'
        chars[self.num_cells - 1] = '#'
        
        for b in self.boxes:
            chars[b] = '$'
        chars[self.worker] = '@'
        
        return ''.join(chars)
    
    def successors(self) -> List[Tuple['SokorridorState', str]]:
        """
        Retourne les successeurs avec l'action effectuée
        Ordre: droite puis gauche (comme demandé dans le PDF)
        """
        succs = []
        
        # MOVE RIGHT
        if self.worker + 1 < self.num_cells and self.worker + 1 not in self.boxes:
            new_state = SokorridorState(self.worker + 1, list(self.boxes), self.num_cells)
            succs.append((new_state, 'move_right'))
        
        # PUSH RIGHT
        if (self.worker + 1 < self.num_cells and 
            self.worker + 1 in self.boxes and 
            self.worker + 2 < self.num_cells and 
            self.worker + 2 not in self.boxes):
            new_boxes = list(self.boxes)
            new_boxes.remove(self.worker + 1)
            new_boxes.append(self.worker + 2)
            new_state = SokorridorState(self.worker + 1, new_boxes, self.num_cells)
            succs.append((new_state, 'push_right'))
        
        # MOVE LEFT
        if self.worker - 1 >= 0 and self.worker - 1 not in self.boxes:
            new_state = SokorridorState(self.worker - 1, list(self.boxes), self.num_cells)
            succs.append((new_state, 'move_left'))
        
        # PUSH LEFT
        if (self.worker - 1 >= 0 and 
            self.worker - 1 in self.boxes and 
            self.worker - 2 >= 0 and 
            self.worker - 2 not in self.boxes):
            new_boxes = list(self.boxes)
            new_boxes.remove(self.worker - 1)
            new_boxes.append(self.worker - 2)
            new_state = SokorridorState(self.worker - 1, new_boxes, self.num_cells)
            succs.append((new_state, 'push_left'))
        
        return succs
    
    def is_goal(self, goals: List[int]) -> bool:
        """Vérifie si toutes les boxes sont sur les goals"""
        return set(self.boxes) == set(goals)


class SokorridorSearchSolver:
    """Résout Sokorridor avec recherche non informée"""
    
    def __init__(self, initial_state: SokorridorState, goals: List[int]):
        self.initial = initial_state
        self.goals = goals
        self.stats = {
            'nodes_explored': 0,
            'nodes_generated': 0,
            'max_frontier_size': 0
        }
    
    def bfs(self) -> Optional[List[Tuple[SokorridorState, str]]]:
        """Breadth-First Search"""
        self._reset_stats()
        
        # Format: (état, chemin_complet)
        frontier = deque([(self.initial, [])])
        explored = {self.initial}
        
        while frontier:
            self.stats['max_frontier_size'] = max(self.stats['max_frontier_size'], len(frontier))
            
            state, path = frontier.popleft()
            self.stats['nodes_explored'] += 1
            
            if state.is_goal(self.goals):
                return path
            
            for succ_state, action in state.successors():
                if succ_state not in explored:
                    explored.add(succ_state)
                    frontier.append((succ_state, path + [(succ_state, action)]))
                    self.stats['nodes_generated'] += 1
        
        return None
    
    def dfs(self, max_depth: Optional[int] = None) -> Optional[List[Tuple[SokorridorState, str]]]:
        """Depth-First Search avec profondeur limitée"""
        self._reset_stats()
        
        # Format: (état, chemin, profondeur)
        frontier = [(self.initial, [], 0)]
        explored = set()
        
        while frontier:
            self.stats['max_frontier_size'] = max(self.stats['max_frontier_size'], len(frontier))
            
            state, path, depth = frontier.pop()  # LIFO
            
            if state in explored:
                continue
            
            explored.add(state)
            self.stats['nodes_explored'] += 1
            
            if state.is_goal(self.goals):
                return path
            
            if max_depth is None or depth < max_depth:
                for succ_state, action in reversed(state.successors()):  # Reversed pour ordre correct
                    if succ_state not in explored:
                        frontier.append((succ_state, path + [(succ_state, action)], depth + 1))
                        self.stats['nodes_generated'] += 1
        
        return None
    
    def iddfs(self, max_depth: int = 30) -> Optional[List[Tuple[SokorridorState, str]]]:
        """Iterative Deepening DFS"""
        print(f"IDDFS: Recherche jusqu'à profondeur {max_depth}...")
        
        for depth in range(max_depth):
            print(f"  Essai profondeur {depth}...", end=' ')
            result = self.dfs(max_depth=depth)
            if result is not None:
                print(f"✓ Solution trouvée!")
                return result
            print(f"({self.stats['nodes_explored']} nœuds)")
        
        return None
    
    def _reset_stats(self):
        """Réinitialise les statistiques"""
        self.stats = {
            'nodes_explored': 0,
            'nodes_generated': 0,
            'max_frontier_size': 0
        }


def print_solution(solution: Optional[List[Tuple[SokorridorState, str]]], initial: SokorridorState):
    """Affiche la solution trouvée"""
    if solution is None:
        print("Pas de solution trouvée!")
        return
    
    print(f"\nSolution trouvée en {len(solution)} étapes:")
    print(f"État initial: {initial.to_string()}")
    
    for i, (state, action) in enumerate(solution):
        symbols = {'move_right': '→', 'move_left': '←', 'push_right': '⇒', 'push_left': '⇐'}
        print(f"  {i+1}. {symbols.get(action, action):2s} → {state.to_string()}")


def main():
    """Teste les algorithmes sur l'exemple du PDF"""
    print("="*60)
    print("SOKORRIDOR - Recherche Non Informée (Séance 3)")
    print("="*60)
    
    # Configuration de l'exemple du PDF: ##. $ @ $.##
    initial = SokorridorState(worker=5, boxes=[2, 8], num_cells=11)
    goals = [1, 9]
    
    print(f"\nConfiguration:")
    print(f"État initial: {initial.to_string()}")
    print(f"Goals: positions {goals}")
    print(f"Représentation: # = mur, . = goal, $ = box, @ = worker")
    
    solver = SokorridorSearchSolver(initial, goals)
    
    # BFS
    print("\n" + "-"*60)
    print("BFS (Breadth-First Search)")
    print("-"*60)
    solution = solver.bfs()
    print_solution(solution, initial)
    print(f"\nStatistiques BFS:")
    print(f"  Nœuds explorés: {solver.stats['nodes_explored']}")
    print(f"  Nœuds générés: {solver.stats['nodes_generated']}")
    print(f"  Taille max frontière: {solver.stats['max_frontier_size']}")
    
    # IDDFS
    print("\n" + "-"*60)
    print("IDDFS (Iterative Deepening DFS)")
    print("-"*60)
    solution = solver.iddfs(max_depth=30)
    print_solution(solution, initial)
    print(f"\nStatistiques IDDFS:")
    print(f"  Nœuds explorés (dernière itération): {solver.stats['nodes_explored']}")
    print(f"  Nœuds générés (dernière itération): {solver.stats['nodes_generated']}")


if __name__ == "__main__":
    main()
