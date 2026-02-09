"""
Résolveur de labyrinthe - Séance 3
Implémente BFS, DFS, IDDFS pour résoudre un labyrinthe
"""
from typing import List, Tuple, Optional, Set
from collections import deque


class Maze:
    """Représente un labyrinthe 2D"""
    
    def __init__(self, grid: List[List[str]]):
        """
        grid: Liste de listes de caractères
        - '.' = case libre
        - '#' = mur
        - 'S' = start (départ)
        - 'G' = goal (but)
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.start = self._find_position('S')
        self.goal = self._find_position('G')
    
    def _find_position(self, char: str) -> Tuple[int, int]:
        """Trouve la position d'un caractère dans le labyrinthe"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == char:
                    return (r, c)
        raise ValueError(f"Caractère '{char}' non trouvé dans le labyrinthe")
    
    def is_valid(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si une position est valide (pas un mur, dans les limites)"""
        r, c = pos
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return False
        return self.grid[r][c] != '#'
    
    def successors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Retourne les successeurs d'une position
        Ordre: haut, droite, bas, gauche (comme demandé)
        """
        r, c = pos
        candidates = [
            (r - 1, c),  # haut
            (r, c + 1),  # droite
            (r + 1, c),  # bas
            (r, c - 1)   # gauche
        ]
        return [p for p in candidates if self.is_valid(p)]
    
    def is_goal(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si une position est le but"""
        return pos == self.goal


class MazeSolver:
    """Résout un labyrinthe avec différents algorithmes"""
    
    def __init__(self, maze: Maze):
        self.maze = maze
        self.stats = {
            'nodes_explored': 0,
            'nodes_generated': 0,
            'max_frontier_size': 0
        }
    
    def bfs(self) -> Optional[List[Tuple[int, int]]]:
        """
        Breadth-First Search (recherche en largeur)
        Utilise une file FIFO
        """
        self._reset_stats()
        
        frontier = deque([(self.maze.start, [self.maze.start])])
        explored = {self.maze.start}
        
        while frontier:
            self.stats['max_frontier_size'] = max(self.stats['max_frontier_size'], len(frontier))
            
            pos, path = frontier.popleft()
            self.stats['nodes_explored'] += 1
            
            if self.maze.is_goal(pos):
                return path
            
            for succ in self.maze.successors(pos):
                if succ not in explored:
                    explored.add(succ)
                    frontier.append((succ, path + [succ]))
                    self.stats['nodes_generated'] += 1
        
        return None  # Pas de solution
    
    def dfs(self, max_depth: Optional[int] = None) -> Optional[List[Tuple[int, int]]]:
        """
        Depth-First Search (recherche en profondeur)
        Utilise une pile LIFO
        max_depth: profondeur maximale (None = illimitée)
        """
        self._reset_stats()
        
        # Format: (position, chemin, profondeur)
        frontier = [(self.maze.start, [self.maze.start], 0)]
        explored = set()
        
        while frontier:
            self.stats['max_frontier_size'] = max(self.stats['max_frontier_size'], len(frontier))
            
            pos, path, depth = frontier.pop()  # LIFO
            
            if pos in explored:
                continue
            
            explored.add(pos)
            self.stats['nodes_explored'] += 1
            
            if self.maze.is_goal(pos):
                return path
            
            if max_depth is None or depth < max_depth:
                for succ in reversed(self.maze.successors(pos)):  # Reversed pour respecter l'ordre
                    if succ not in explored:
                        frontier.append((succ, path + [succ], depth + 1))
                        self.stats['nodes_generated'] += 1
        
        return None
    
    def iddfs(self, max_depth: int = 50) -> Optional[List[Tuple[int, int]]]:
        """
        Iterative Deepening DFS
        DFS avec profondeur maximale itérative
        """
        for depth in range(max_depth):
            result = self.dfs(max_depth=depth)
            if result is not None:
                return result
        
        return None
    
    def _reset_stats(self):
        """Réinitialise les statistiques"""
        self.stats = {
            'nodes_explored': 0,
            'nodes_generated': 0,
            'max_frontier_size': 0
        }


def create_example_maze() -> Maze:
    """
    Crée le labyrinthe de l'exemple (page 8 du PDF)
    
    4  [S] [ ] [ ] [ ]
    3  [ ] [#] [ ] [#]
    2  [ ] [#] [ ] [ ]
    1  [ ] [G] [ ] [ ]
       A   B   C   D
    """
    grid = [
        ['S', '.', '.', '.'],  # ligne 4
        ['.', '#', '.', '#'],  # ligne 3
        ['.', '#', '.', '.'],  # ligne 2
        ['.', 'G', '.', '.']   # ligne 1
    ]
    return Maze(grid)


def print_maze_with_path(maze: Maze, path: Optional[List[Tuple[int, int]]]):
    """Affiche le labyrinthe avec le chemin trouvé"""
    if path is None:
        print("Pas de solution trouvée!")
        return
    
    path_set = set(path)
    
    print("\nLabyrinthe avec chemin:")
    for r in range(maze.rows):
        row_str = ""
        for c in range(maze.cols):
            pos = (r, c)
            if maze.grid[r][c] == 'S':
                row_str += "S "
            elif maze.grid[r][c] == 'G':
                row_str += "G "
            elif maze.grid[r][c] == '#':
                row_str += "# "
            elif pos in path_set:
                row_str += "* "
            else:
                row_str += ". "
        print(row_str)
    
    print(f"\nLongueur du chemin: {len(path) - 1} étapes")
    print(f"Chemin: {' → '.join([f'({r},{c})' for r, c in path])}")


def main():
    """Teste les algorithmes sur l'exemple du PDF"""
    print("="*60)
    print("RÉSOLUTION DE LABYRINTHE - Séance 3")
    print("="*60)
    
    maze = create_example_maze()
    solver = MazeSolver(maze)
    
    # BFS
    print("\n--- BFS (Breadth-First Search) ---")
    path = solver.bfs()
    print_maze_with_path(maze, path)
    print(f"Nœuds explorés: {solver.stats['nodes_explored']}")
    print(f"Nœuds générés: {solver.stats['nodes_generated']}")
    print(f"Taille max frontière: {solver.stats['max_frontier_size']}")
    
    # DFS
    print("\n--- DFS (Depth-First Search) ---")
    path = solver.dfs()
    print_maze_with_path(maze, path)
    print(f"Nœuds explorés: {solver.stats['nodes_explored']}")
    print(f"Nœuds générés: {solver.stats['nodes_generated']}")
    
    # IDDFS
    print("\n--- IDDFS (Iterative Deepening DFS) ---")
    path = solver.iddfs()
    print_maze_with_path(maze, path)
    print(f"Nœuds explorés: {solver.stats['nodes_explored']}")
    print(f"Nœuds générés: {solver.stats['nodes_generated']}")


if __name__ == "__main__":
    main()
