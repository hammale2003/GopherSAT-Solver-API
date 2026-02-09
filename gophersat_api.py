from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
import subprocess
import tempfile
import os
from graph_coloring import GraphColoringSAT
from sudoku_solver import SudokuSAT
from sokoban_solver import SokobanSAT
from sokoban_simulator import SokobanSimulator
from maze_solver import Maze, MazeSolver, create_example_maze
from sokorridor_search import SokorridorState, SokorridorSearchSolver
from puzzle_solver import PuzzleState, AStarSolver

app = FastAPI(title="GopherSAT Solver API - SAT Problems Solver")

# CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOPHERSAT_PATH = r"C:\Users\hp\Downloads\gophersat\gophersat.exe"

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class GraphColoringRequest(BaseModel):
    """
    Requête pour le coloriage de graphe
    
    V: ensemble des sommets
    E: ensemble des arêtes  
    K: ensemble des couleurs
    """
    V: List[str]  # Sommets
    E: List[List[str]]  # Arêtes (liste de paires [u, v])
    K: List[str]  # Couleurs
    
    class Config:
        json_schema_extra = {
            "example": {
                "V": ["A", "B", "C", "D"],
                "E": [["A", "B"], ["A", "C"], ["B", "C"], ["B", "D"], ["C", "D"]],
                "K": ["r", "v", "b"]
            }
        }

class SudokuRequest(BaseModel):
    """
    Requête pour résoudre un Sudoku
    
    grid: Grille 9x9 avec 0 pour les cases vides, 1-9 pour les cases remplies
    """
    grid: List[List[int]]
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }

class SokobanRequest(BaseModel):
    """
    Requête pour résoudre un Sokorridor
    
    initial_state: État initial {worker: int, boxes: List[int]}
    goals: Positions des objectifs
    T: Horizon temporel (optionnel, défaut 15)
    num_cells: Nombre de cases (optionnel, défaut 11)
    """
    initial_state: dict
    goals: List[int]
    T: int = 15
    num_cells: int = 11
    
    class Config:
        json_schema_extra = {
            "example": {
                "initial_state": {"worker": 6, "boxes": [2, 9]},
                "goals": [1, 10],
                "T": 15,
                "num_cells": 11
            }
        }

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "GopherSAT Solver API - SAT Problems Solver",
        "description": "API pour résoudre des problèmes SAT: coloriage de graphe, Sudoku, et Sokoban",
        "endpoints": {
            "POST /solve": "Résoudre un fichier CNF",
            "POST /graph-coloring": "Coloriage de graphe - prend V, E, K et retourne φ",
            "POST /sudoku": "Résoudre un Sudoku - prend une grille 9x9",
            "POST /sokoban": "Résoudre un Sokorridor - planification à horizon fini",
            "GET /visualizer": "Interface web pour visualiser les résultats",
            "GET /docs": "Documentation interactive Swagger",
            "GET /health": "Vérifier l'état de GopherSAT"
        },
        "examples": {
            "graph_coloring": {
                "V": ["A", "B", "C", "D"],
                "E": [["A", "B"], ["A", "C"], ["B", "C"], ["B", "D"], ["C", "D"]],
                "K": ["r", "v", "b"]
            },
            "sudoku": {
                "grid": "9x9 array with 0 for empty cells"
            },
            "sokoban": {
                "initial_state": {"worker": 6, "boxes": [2, 9]},
                "goals": [1, 10],
                "T": 15
            }
        }
    }

@app.get("/visualizer", response_class=HTMLResponse)
async def visualizer():
    """Sert l'interface de visualisation HTML"""
    html_file = os.path.join(os.path.dirname(__file__), "visualizer.html")
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <!DOCTYPE html>
        <html><body>
        <h1>Erreur</h1>
        <p>Le fichier visualizer.html n'a pas été trouvé.</p>
        <p>Assurez-vous que visualizer.html est dans le même répertoire que gophersat_api.py</p>
        </body></html>
        """

@app.post("/solve")
async def solve_cnf(file: UploadFile = File(...)):
    """
    Résout un fichier CNF avec GopherSAT
    
    Args:
        file: Fichier CNF à résoudre
        
    Returns:
        Solution SAT avec format présentable
    """
    # Valider l'extension du fichier
    if not file.filename.endswith('.cnf'):
        raise HTTPException(status_code=400, detail="Le fichier doit avoir l'extension .cnf")
    
    # Vérifier que GopherSAT existe
    if not os.path.exists(GOPHERSAT_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"GopherSAT non trouvé à : {GOPHERSAT_PATH}"
        )
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.cnf', delete=False) as temp_file:
        temp_path = temp_file.name
        content = await file.read()
        temp_file.write(content)
    
    try:
        # Exécuter GopherSAT
        result = subprocess.run(
            [GOPHERSAT_PATH, temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parser la sortie
        stdout_lines = result.stdout.strip().split('\n')
        
        status = "UNKNOWN"
        solution = []
        comments = []
        
        for line in stdout_lines:
            line = line.strip()
            if line.startswith('s '):
                status = line[2:].strip()
            elif line.startswith('v '):
                vars_str = line[2:].strip()
                solution.extend(vars_str.split())
            elif line.startswith('c '):
                comments.append(line[2:].strip())
        
        # Nettoyer la solution (retirer le 0 final)
        if solution and solution[-1] == '0':
            solution = solution[:-1]
        
        # Formatter les assignments
        assignments = {}
        if solution:
            for var in solution:
                if var != '0':
                    var_num = abs(int(var))
                    assignments[f"x{var_num}"] = int(var) > 0
        
        response = {
            "status": "success",
            "filename": file.filename,
            "result": {
                "satisfiable": status == "SATISFIABLE",
                "status": status,
                "solution": {
                    "raw": " ".join(solution) if solution else None,
                    "assignments": assignments if assignments else None,
                    "total_variables": len(assignments) if assignments else 0
                }
            },
            "execution": {
                "return_code": result.returncode,
                "comments": comments if comments else None,
                "errors": result.stderr if result.stderr else None
            }
        }
        
        return JSONResponse(content=response)
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout après 60 secondes")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'exécution: {str(e)}")
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/graph-coloring")
async def solve_graph_coloring(request: GraphColoringRequest):
    """
    Résout le problème de coloriage de graphe
    
    Prend en entrée les ensembles V, E, K et retourne un coloriage φ : V → K s'il existe
    
    Args:
        V: Liste des sommets du graphe
        E: Liste des arêtes (paires de sommets)
        K: Liste des couleurs disponibles
        
    Returns:
        - satisfiable: bool - si un coloriage existe
        - phi: Dict[str, str] - le coloriage φ : V → K (None si non satisfiable)
        - cnf_file: str - le fichier CNF généré
        - stats: Dict - statistiques sur le problème
        
    Example:
        {
            "V": ["A", "B", "C", "D"],
            "E": [["A", "B"], ["A", "C"], ["B", "C"], ["B", "D"], ["C", "D"]],
            "K": ["r", "v", "b"]
        }
        
        Retourne:
        {
            "satisfiable": true,
            "phi": {"A": "r", "B": "v", "C": "b", "D": "r"},
            "message": "Coloriage trouvé: φ : V → K où φ = {...}",
            "cnf_file": "c Graph coloring...",
            "stats": {...}
        }
    """
    # Vérifier que GopherSAT existe
    if not os.path.exists(GOPHERSAT_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"GopherSAT non trouvé à : {GOPHERSAT_PATH}"
        )
    
    # Convertir E en tuples pour le traitement
    edges = [(e[0], e[1]) for e in request.E]
    
    # Créer le solveur
    solver = GraphColoringSAT(GOPHERSAT_PATH)
    
    # Résoudre le problème
    result = solver.solve(
        vertices=request.V,
        edges=edges,
        colors=request.K
    )
    
    # Vérifier s'il y a une erreur
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return JSONResponse(content=result)

@app.post("/sudoku")
async def solve_sudoku(request: SudokuRequest):
    """
    Résout un Sudoku en utilisant SAT
    
    Args:
        grid: Grille 9x9 avec 0 pour les cases vides, 1-9 pour les cases remplies
        
    Returns:
        - satisfiable: bool - si le Sudoku est résolvable
        - solution: List[List[int]] - la grille résolue (None si non résolvable)
        - cnf_file: str - le fichier CNF généré
        - stats: Dict - statistiques
        
    Example:
        {
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
        
        Retourne:
        {
            "satisfiable": true,
            "solution": [[5,3,4,6,7,8,9,1,2], ...],
            "message": "Sudoku résolu avec succès",
            ...
        }
    """
    # Vérifier que GopherSAT existe
    if not os.path.exists(GOPHERSAT_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"GopherSAT non trouvé à : {GOPHERSAT_PATH}"
        )
    
    # Créer le solveur
    solver = SudokuSAT(GOPHERSAT_PATH)
    
    # Résoudre le Sudoku
    result = solver.solve(grid=request.grid)
    
    # Vérifier s'il y a une erreur
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return JSONResponse(content=result)

@app.post("/sokoban")
async def solve_sokoban(request: SokobanRequest):
    """
    Résout un problème de Sokorridor (planification)
    
    Args:
        initial_state: État initial {worker: int, boxes: List[int]}
        goals: Positions des objectifs
        T: Horizon temporel (défaut 15)
        num_cells: Nombre de cases (défaut 11)
        
    Returns:
        - satisfiable: bool - si un plan existe
        - plan: List[Tuple[int, str]] - séquence d'actions
        - visualization: List[str] - images de l'exécution
        
    Example:
        {
            "initial_state": {"worker": 6, "boxes": [2, 9]},
            "goals": [1, 10],
            "T": 15,
            "num_cells": 11
        }
        
        État initial: #. $   @  $.#
        But: déplacer les caisses sur les objectifs (positions 1 et 10)
    """
    # Vérifier que GopherSAT existe
    if not os.path.exists(GOPHERSAT_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"GopherSAT non trouvé à : {GOPHERSAT_PATH}"
        )
    
    # Créer le solveur
    solver = SokobanSAT(GOPHERSAT_PATH)
    
    # Résoudre
    result = solver.solve(
        initial_state=request.initial_state,
        goals=request.goals,
        T=request.T,
        num_cells=request.num_cells
    )
    
    # Vérifier s'il y a une erreur
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Si satisfiable, simuler et visualiser
    if result["satisfiable"]:
        simulator = SokobanSimulator(num_cells=request.num_cells)
        simulator.set_initial_state(
            request.initial_state['worker'],
            request.initial_state['boxes'],
            request.goals
        )
        
        # Exécuter le plan
        plan_result = simulator.execute_plan(result['plan'])
        
        # Générer les visualisations
        try:
            visualizations = simulator.visualize_plan_execution(plan_result)
            animated_gif = simulator.create_animated_gif(plan_result, duration=500)
            result['visualizations'] = visualizations
            result['animated_gif'] = animated_gif
            result['simulation'] = {
                'success': plan_result['success'],
                'message': plan_result['message'],
                'goal_reached': plan_result['goal_reached']
            }
        except Exception as e:
            result['visualizations'] = None
            result['animated_gif'] = None
            result['simulation'] = {'error': str(e)}
    
    return JSONResponse(content=result)

@app.get("/health")
async def health_check():
    """Vérifie si GopherSAT est accessible"""
    gophersat_exists = os.path.exists(GOPHERSAT_PATH)
    return {
        "status": "healthy" if gophersat_exists else "unhealthy",
        "gophersat_path": GOPHERSAT_PATH,
        "gophersat_found": gophersat_exists
    }

# ============================================================================
# SÉANCE 3 - PLANIFICATION ET RECHERCHE
# ============================================================================

@app.get("/maze/{algorithm}")
async def solve_maze(algorithm: str):
    """
    Résout le labyrinthe avec l'algorithme spécifié
    
    Algorithmes disponibles : bfs, dfs, iddfs
    """
    if algorithm not in ['bfs', 'dfs', 'iddfs']:
        raise HTTPException(status_code=400, detail="Algorithme invalide. Utilisez : bfs, dfs, iddfs")
    
    try:
        maze = create_example_maze()
        solver = MazeSolver(maze)
        
        if algorithm == 'bfs':
            path = solver.bfs()
        elif algorithm == 'dfs':
            path = solver.dfs()
        else:  # iddfs
            path = solver.iddfs()
        
        return {
            "algorithm": algorithm,
            "path": path,
            "stats": solver.stats,
            "success": path is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SokorridorRequest(BaseModel):
    """Requête pour Sokorridor"""
    worker: int
    boxes: List[int]
    goals: List[int]


@app.post("/sokorridor/{algorithm}")
async def solve_sokorridor(algorithm: str, request: SokorridorRequest):
    """
    Résout le Sokorridor avec l'algorithme spécifié
    
    Algorithmes disponibles : bfs, iddfs
    """
    if algorithm not in ['bfs', 'iddfs']:
        raise HTTPException(status_code=400, detail="Algorithme invalide. Utilisez : bfs, iddfs")
    
    try:
        initial = SokorridorState(request.worker, request.boxes, num_cells=11)
        solver = SokorridorSearchSolver(initial, request.goals)
        
        if algorithm == 'bfs':
            solution = solver.bfs()
        else:  # iddfs
            solution = solver.iddfs()
        
        return {
            "algorithm": algorithm,
            "solution": solution,
            "stats": solver.stats,
            "success": solution is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PuzzleRequest(BaseModel):
    """Requête pour le Taquin"""
    initial: List[List[int]]
    goal: List[List[int]]


@app.post("/puzzle/{heuristic}")
async def solve_puzzle(heuristic: str, request: PuzzleRequest):
    """
    Résout le Taquin avec A* et l'heuristique spécifiée
    
    Heuristiques disponibles : manhattan, misplaced, euclidean
    """
    if heuristic not in ['manhattan', 'misplaced', 'euclidean']:
        raise HTTPException(status_code=400, detail="Heuristique invalide. Utilisez : manhattan, misplaced, euclidean")
    
    try:
        initial = PuzzleState(request.initial)
        goal = PuzzleState(request.goal)
        
        solver = AStarSolver(initial, goal, heuristic=heuristic)
        solution = solver.solve()
        
        # Convertir la solution en format sérialisable
        if solution:
            solution_serializable = [
                (None, action) for _, action in solution  # On garde juste les actions
            ]
        else:
            solution_serializable = None
        
        return {
            "heuristic": heuristic,
            "solution": solution_serializable,
            "stats": solver.stats,
            "success": solution is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visualizer-seance3")
async def get_visualizer_seance3():
    """Retourne le visualiseur HTML pour la Séance 3"""
    try:
        with open('/mnt/user-data/outputs/visualizer_seance3.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Visualiseur non trouvé")


# ============================================================================
# LANCEMENT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Lancement de l'API GopherSAT")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)