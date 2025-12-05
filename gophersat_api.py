from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import subprocess
import tempfile
import os
from graph_coloring import GraphColoringSAT
from sudoku_solver import SudokuSAT

app = FastAPI(title="GopherSAT Solver API - Coloriage de Graphe & Sudoku")

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

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "GopherSAT Solver API - Coloriage de Graphe & Sudoku",
        "description": "API pour résoudre des problèmes SAT, de coloriage de graphe et de Sudoku",
        "endpoints": {
            "POST /solve": "Résoudre un fichier CNF",
            "POST /graph-coloring": "Coloriage de graphe - prend V, E, K et retourne φ",
            "POST /sudoku": "Résoudre un Sudoku - prend une grille 9x9",
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
            }
        }
    }

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
# LANCEMENT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Lancement de l'API GopherSAT")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)