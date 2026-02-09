"""
Taquin (8-Puzzle) Solver avec A*
Séance 3 - Recherche informée
"""
from typing import List, Tuple, Optional
import heapq


class PuzzleState:
    """État du taquin 3x3"""
    
    def __init__(self, board: List[List[int]], parent=None, action=None, g=0):
        """
        board: grille 3x3 avec 0 représentant la case vide
        parent: état parent
        action: action qui a mené à cet état
        g: coût depuis l'initial
        """
        self.board = [row[:] for row in board]  # Copie
        self.parent = parent
        self.action = action
        self.g = g
        self.empty_pos = self._find_empty()
        
    def _find_empty(self) -> Tuple[int, int]:
        """Trouve la position de la case vide (0)"""
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == 0:
                    return (r, c)
        raise ValueError("Pas de case vide!")
    
    def __eq__(self, other):
        return self.board == other.board
    
    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))
    
    def __repr__(self):
        return '\n'.join([' '.join([str(x) if x != 0 else '∅' for x in row]) for row in self.board])
    
    def __lt__(self, other):
        # Pour heapq
        return False
    
    def successors(self) -> List['PuzzleState']:
        """Génère les successeurs (haut, droite, bas, gauche)"""
        r, c = self.empty_pos
        succs = []
        
        moves = [
            ((-1, 0), 'haut'),
            ((0, 1), 'droite'),
            ((1, 0), 'bas'),
            ((0, -1), 'gauche')
        ]
        
        for (dr, dc), action in moves:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_board = [row[:] for row in self.board]
                # Échanger la case vide avec la case adjacente
                new_board[r][c], new_board[nr][nc] = new_board[nr][nc], new_board[r][c]
                succs.append(PuzzleState(new_board, parent=self, action=action, g=self.g + 1))
        
        return succs
    
    def is_goal(self, goal_state: 'PuzzleState') -> bool:
        """Vérifie si cet état est le but"""
        return self.board == goal_state.board
    
    def get_path(self) -> List[Tuple['PuzzleState', str]]:
        """Reconstruit le chemin depuis l'initial"""
        path = []
        state = self
        while state.parent is not None:
            path.append((state, state.action))
            state = state.parent
        return list(reversed(path))


class Heuristic:
    """Différentes heuristiques pour le taquin"""
    
    @staticmethod
    def manhattan_distance(state: PuzzleState, goal: PuzzleState) -> int:
        """
        Distance de Manhattan
        Somme des distances de chaque tuile vers sa position finale
        """
        distance = 0
        goal_positions = {}
        
        # Trouver les positions dans le but
        for r in range(3):
            for c in range(3):
                val = goal.board[r][c]
                if val != 0:
                    goal_positions[val] = (r, c)
        
        # Calculer la distance pour chaque tuile
        for r in range(3):
            for c in range(3):
                val = state.board[r][c]
                if val != 0:
                    gr, gc = goal_positions[val]
                    distance += abs(r - gr) + abs(c - gc)
        
        return distance
    
    @staticmethod
    def misplaced_tiles(state: PuzzleState, goal: PuzzleState) -> int:
        """
        Nombre de tuiles mal placées
        """
        count = 0
        for r in range(3):
            for c in range(3):
                if state.board[r][c] != 0 and state.board[r][c] != goal.board[r][c]:
                    count += 1
        return count
    
    @staticmethod
    def euclidean_distance(state: PuzzleState, goal: PuzzleState) -> float:
        """
        Distance euclidienne
        """
        distance = 0.0
        goal_positions = {}
        
        for r in range(3):
            for c in range(3):
                val = goal.board[r][c]
                if val != 0:
                    goal_positions[val] = (r, c)
        
        for r in range(3):
            for c in range(3):
                val = state.board[r][c]
                if val != 0:
                    gr, gc = goal_positions[val]
                    distance += ((r - gr)**2 + (c - gc)**2) ** 0.5
        
        return distance


class AStarSolver:
    """Résout le taquin avec A*"""
    
    def __init__(self, initial: PuzzleState, goal: PuzzleState, heuristic='manhattan'):
        self.initial = initial
        self.goal = goal
        
        heuristics = {
            'manhattan': Heuristic.manhattan_distance,
            'misplaced': Heuristic.misplaced_tiles,
            'euclidean': Heuristic.euclidean_distance
        }
        self.h_func = heuristics.get(heuristic, Heuristic.manhattan_distance)
        self.heuristic_name = heuristic
        
        self.stats = {
            'nodes_explored': 0,
            'nodes_generated': 0,
            'max_frontier_size': 0
        }
    
    def solve(self) -> Optional[List[Tuple[PuzzleState, str]]]:
        """Résout avec A*"""
        self.stats = {'nodes_explored': 0, 'nodes_generated': 0, 'max_frontier_size': 0}
        
        # Frontière: (f, compteur, état)
        # f = g + h
        # compteur pour départager les états avec même f
        counter = 0
        h_initial = self.h_func(self.initial, self.goal)
        frontier = [(h_initial, counter, self.initial)]
        explored = set()
        
        while frontier:
            self.stats['max_frontier_size'] = max(self.stats['max_frontier_size'], len(frontier))
            
            f, _, state = heapq.heappop(frontier)
            
            if state in explored:
                continue
            
            explored.add(state)
            self.stats['nodes_explored'] += 1
            
            if state.is_goal(self.goal):
                return state.get_path()
            
            for succ in state.successors():
                if succ not in explored:
                    h = self.h_func(succ, self.goal)
                    f = succ.g + h
                    counter += 1
                    heapq.heappush(frontier, (f, counter, succ))
                    self.stats['nodes_generated'] += 1
        
        return None


def create_example_states() -> Tuple[PuzzleState, PuzzleState]:
    """
    Crée les états de l'exemple du PDF (page 12)
    
    Initial:          Goal:
    5 8 7            1 2 3
    4 ∅ 3            4 5 6
    6 2 1            7 8 ∅
    """
    initial = PuzzleState([
        [5, 8, 7],
        [4, 0, 3],
        [6, 2, 1]
    ])
    
    goal = PuzzleState([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ])
    
    return initial, goal


def print_solution(solution: Optional[List[Tuple[PuzzleState, str]]], initial: PuzzleState):
    """Affiche la solution"""
    if solution is None:
        print("Pas de solution trouvée!")
        return
    
    print(f"\nSolution trouvée en {len(solution)} étapes:")
    print("\nÉtat initial:")
    print(initial)
    print()
    
    for i, (state, action) in enumerate(solution):
        print(f"Étape {i+1}: {action}")
        print(state)
        print()


def main():
    """Teste A* avec différentes heuristiques"""
    print("="*60)
    print("TAQUIN (8-PUZZLE) - A* avec heuristiques")
    print("="*60)
    
    initial, goal = create_example_states()
    
    print("\nÉtat initial:")
    print(initial)
    print("\nÉtat but:")
    print(goal)
    
    heuristics = ['manhattan', 'misplaced', 'euclidean']
    
    for h_name in heuristics:
        print("\n" + "="*60)
        print(f"A* avec heuristique: {h_name.upper()}")
        print("="*60)
        
        solver = AStarSolver(initial, goal, heuristic=h_name)
        solution = solver.solve()
        
        if solution:
            print(f"\n✓ Solution trouvée en {len(solution)} étapes")
            print(f"  Nœuds explorés: {solver.stats['nodes_explored']}")
            print(f"  Nœuds générés: {solver.stats['nodes_generated']}")
            print(f"  Taille max frontière: {solver.stats['max_frontier_size']}")
            
            print("\nActions:", " → ".join([action for _, action in solution]))
        else:
            print("\n✗ Pas de solution trouvée")
    
    # Afficher la solution détaillée avec Manhattan
    print("\n" + "="*60)
    print("SOLUTION DÉTAILLÉE (Manhattan)")
    print("="*60)
    solver = AStarSolver(initial, goal, heuristic='manhattan')
    solution = solver.solve()
    print_solution(solution, initial)


if __name__ == "__main__":
    main()
