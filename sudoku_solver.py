"""
Module pour résoudre le Sudoku avec SAT
"""
import tempfile
import subprocess
import os
import io
import base64
from typing import List, Dict, Optional
import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import matplotlib.pyplot as plt
import numpy as np


class SudokuSAT:
    """Résout le Sudoku en utilisant un solveur SAT"""
    
    def __init__(self, gophersat_path: str):
        self.gophersat_path = gophersat_path
        self.size = 9  # Taille standard du Sudoku 9x9
        self.box_size = 3  # Taille des sous-grilles 3x3
        
    def encode_variable(self, row: int, col: int, value: int) -> int:
        """
        Encode une variable (ligne, colonne, valeur) en un entier unique
        Variable x_{r,c,v} : la cellule (r,c) contient la valeur v
        
        Formule: (row * 9 * 9) + (col * 9) + value
        Les indices commencent à 1
        """
        return (row - 1) * self.size * self.size + (col - 1) * self.size + value
    
    def decode_variable(self, var_num: int) -> tuple:
        """Décode un numéro de variable en (ligne, colonne, valeur)"""
        var_num -= 1  # Retour à l'indexation 0
        row = (var_num // (self.size * self.size)) + 1
        col = ((var_num % (self.size * self.size)) // self.size) + 1
        value = (var_num % self.size) + 1
        return row, col, value
    
    def generate_cnf(self, grid: List[List[int]]) -> tuple:
        """
        Génère le fichier CNF pour le Sudoku
        
        Contraintes:
        1. Chaque cellule contient au moins un chiffre (1-9)
        2. Chaque cellule contient au plus un chiffre
        3. Chaque ligne contient chaque chiffre exactement une fois
        4. Chaque colonne contient chaque chiffre exactement une fois
        5. Chaque sous-grille 3x3 contient chaque chiffre exactement une fois
        6. Contraintes initiales (cellules pré-remplies)
        
        Args:
            grid: Grille 9x9 avec 0 pour les cases vides, 1-9 pour les cases remplies
            
        Returns:
            (cnf_content, nb_variables, nb_clauses)
        """
        clauses = []
        
        # Nombre total de variables: 9 * 9 * 9 = 729
        nb_variables = self.size * self.size * self.size
        
        # En-têtes avec commentaires
        cnf_lines = []
        cnf_lines.append("c Sudoku SAT encoding")
        cnf_lines.append("c")
        cnf_lines.append("c Variable encoding: x_{r,c,v} = (r-1)*81 + (c-1)*9 + v")
        cnf_lines.append("c   where r,c,v in {1..9}")
        cnf_lines.append("c   x_{r,c,v} = true means cell (r,c) contains value v")
        cnf_lines.append("c")
        cnf_lines.append("c Initial grid:")
        for i, row in enumerate(grid, 1):
            row_str = " ".join(str(x) if x != 0 else "." for x in row)
            cnf_lines.append(f"c   Row {i}: {row_str}")
        cnf_lines.append("c")
        
        # Contrainte 1: Chaque cellule contient au moins un chiffre
        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):
                clause = []
                for value in range(1, self.size + 1):
                    var = self.encode_variable(row, col, value)
                    clause.append(var)
                clauses.append(clause)
        
        # Contrainte 2: Chaque cellule contient au plus un chiffre
        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):
                for v1 in range(1, self.size + 1):
                    for v2 in range(v1 + 1, self.size + 1):
                        var1 = self.encode_variable(row, col, v1)
                        var2 = self.encode_variable(row, col, v2)
                        clauses.append([-var1, -var2])
        
        # Contrainte 3: Chaque ligne contient chaque chiffre exactement une fois
        for row in range(1, self.size + 1):
            for value in range(1, self.size + 1):
                # Au moins une fois
                clause = []
                for col in range(1, self.size + 1):
                    var = self.encode_variable(row, col, value)
                    clause.append(var)
                clauses.append(clause)
                
                # Au plus une fois
                for c1 in range(1, self.size + 1):
                    for c2 in range(c1 + 1, self.size + 1):
                        var1 = self.encode_variable(row, c1, value)
                        var2 = self.encode_variable(row, c2, value)
                        clauses.append([-var1, -var2])
        
        # Contrainte 4: Chaque colonne contient chaque chiffre exactement une fois
        for col in range(1, self.size + 1):
            for value in range(1, self.size + 1):
                # Au moins une fois
                clause = []
                for row in range(1, self.size + 1):
                    var = self.encode_variable(row, col, value)
                    clause.append(var)
                clauses.append(clause)
                
                # Au plus une fois
                for r1 in range(1, self.size + 1):
                    for r2 in range(r1 + 1, self.size + 1):
                        var1 = self.encode_variable(r1, col, value)
                        var2 = self.encode_variable(r2, col, value)
                        clauses.append([-var1, -var2])
        
        # Contrainte 5: Chaque sous-grille 3x3 contient chaque chiffre exactement une fois
        for box_row in range(3):
            for box_col in range(3):
                for value in range(1, self.size + 1):
                    # Au moins une fois dans la box
                    clause = []
                    for r in range(3):
                        for c in range(3):
                            row = box_row * 3 + r + 1
                            col = box_col * 3 + c + 1
                            var = self.encode_variable(row, col, value)
                            clause.append(var)
                    clauses.append(clause)
                    
                    # Au plus une fois dans la box
                    cells = []
                    for r in range(3):
                        for c in range(3):
                            row = box_row * 3 + r + 1
                            col = box_col * 3 + c + 1
                            cells.append((row, col))
                    
                    for i in range(len(cells)):
                        for j in range(i + 1, len(cells)):
                            r1, c1 = cells[i]
                            r2, c2 = cells[j]
                            var1 = self.encode_variable(r1, c1, value)
                            var2 = self.encode_variable(r2, c2, value)
                            clauses.append([-var1, -var2])
        
        # Contrainte 6: Cellules pré-remplies
        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):
                value = grid[row - 1][col - 1]
                if value != 0:  # Cellule pré-remplie
                    var = self.encode_variable(row, col, value)
                    clauses.append([var])
        
        nb_clauses = len(clauses)
        
        # Ligne p cnf
        cnf_lines.append(f"p cnf {nb_variables} {nb_clauses}")
        
        # Ajouter toutes les clauses
        for clause in clauses:
            clause_str = " ".join(map(str, clause)) + " 0"
            cnf_lines.append(clause_str)
        
        cnf_content = "\n".join(cnf_lines)
        return cnf_content, nb_variables, nb_clauses
    
    def plot_sudoku(self, initial_grid: List[List[int]], 
                    solved_grid: List[List[int]]) -> str:
        """
        Génère une visualisation du Sudoku résolu
        
        Args:
            initial_grid: Grille initiale (avec 0 pour cases vides)
            solved_grid: Grille résolue
            
        Returns:
            Image encodée en base64
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Fonction pour dessiner une grille
        def draw_grid(ax, grid, title, show_colors=False):
            ax.set_xlim(0, 9)
            ax.set_ylim(0, 9)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
            
            # Dessiner les lignes de la grille
            for i in range(10):
                lw = 3 if i % 3 == 0 else 0.5
                ax.plot([0, 9], [i, i], 'k-', linewidth=lw)
                ax.plot([i, i], [0, 9], 'k-', linewidth=lw)
            
            # Remplir les cellules
            for i in range(9):
                for j in range(9):
                    val = grid[i][j]
                    if val != 0:
                        # Colorier le fond des cellules pré-remplies
                        if show_colors and initial_grid[i][j] != 0:
                            rect = plt.Rectangle((j, 8-i), 1, 1, 
                                                facecolor='lightblue', 
                                                edgecolor='none')
                            ax.add_patch(rect)
                        
                        # Texte
                        color = 'black' if initial_grid[i][j] != 0 else 'blue'
                        weight = 'bold' if initial_grid[i][j] != 0 else 'normal'
                        ax.text(j + 0.5, 8 - i + 0.5, str(val),
                               ha='center', va='center',
                               fontsize=20, color=color, fontweight=weight)
        
        # Grille initiale
        draw_grid(ax1, initial_grid, "Grille Initiale", show_colors=False)
        
        # Grille résolue
        draw_grid(ax2, solved_grid, "Grille Résolue", show_colors=True)
        
        # Ajouter une légende
        legend_text = "Noir/Fond bleu: Cases initiales\nBleu: Cases calculées"
        fig.text(0.5, 0.02, legend_text, ha='center', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def solve(self, grid: List[List[int]]) -> Dict:
        """
        Résout le Sudoku
        
        Args:
            grid: Grille 9x9 avec 0 pour les cases vides, 1-9 pour les cases remplies
            
        Returns:
            Dictionnaire avec:
            - satisfiable: bool
            - solution: List[List[int]] ou None (la grille résolue)
            - cnf_file: str (le fichier CNF généré)
            - stats: Dict (statistiques)
        """
        # Validation
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            return {"error": "La grille doit être 9x9"}
        
        # Vérifier que toutes les valeurs sont entre 0 et 9
        for row in grid:
            for val in row:
                if not (0 <= val <= 9):
                    return {"error": f"Valeur invalide: {val}. Les valeurs doivent être entre 0 (vide) et 9"}
        
        # Générer le CNF
        try:
            cnf_content, nb_vars, nb_clauses = self.generate_cnf(grid)
        except Exception as e:
            return {"error": f"Erreur lors de la génération du CNF: {str(e)}"}
        
        # Créer un fichier temporaire avec encodage UTF-8
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False, newline='\n', encoding='utf-8') as temp_file:
            temp_path = temp_file.name
            temp_file.write(cnf_content)
            temp_file.write('\n')
            temp_file.flush()
        
        try:
            # Exécuter GopherSAT
            result = subprocess.run(
                [self.gophersat_path, temp_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parser la sortie
            stdout_lines = result.stdout.strip().split('\n')
            
            status = "UNKNOWN"
            solution_vars = []
            
            for line in stdout_lines:
                line = line.strip()
                if line.startswith('s '):
                    status = line[2:].strip()
                elif line.startswith('v '):
                    vars_str = line[2:].strip()
                    solution_vars.extend(vars_str.split())
            
            # Nettoyer la solution
            if solution_vars and solution_vars[-1] == '0':
                solution_vars = solution_vars[:-1]
            
            if status == "SATISFIABLE":
                # Décoder la solution
                solved_grid = [[0] * 9 for _ in range(9)]
                
                for var_str in solution_vars:
                    if var_str != '0':
                        var_num = int(var_str)
                        if var_num > 0:  # Variable vraie
                            row, col, value = self.decode_variable(var_num)
                            solved_grid[row - 1][col - 1] = value
                
                # Générer la visualisation
                try:
                    plot_image = self.plot_sudoku(grid, solved_grid)
                except Exception as e:
                    plot_image = None
                    print(f"Erreur lors de la génération du plot: {e}")
                
                return {
                    "satisfiable": True,
                    "solution": solved_grid,
                    "message": "Sudoku résolu avec succès",
                    "plot": plot_image,  # Image base64
                    "cnf_file": cnf_content,
                    "stats": {
                        "nb_variables": nb_vars,
                        "nb_clauses": nb_clauses,
                        "filled_cells": sum(1 for row in grid for val in row if val != 0),
                        "empty_cells": sum(1 for row in grid for val in row if val == 0)
                    }
                }
            else:
                return {
                    "satisfiable": False,
                    "solution": None,
                    "message": "Aucune solution n'existe pour ce Sudoku (grille invalide)",
                    "cnf_file": cnf_content,
                    "stats": {
                        "nb_variables": nb_vars,
                        "nb_clauses": nb_clauses,
                        "filled_cells": sum(1 for row in grid for val in row if val != 0),
                        "empty_cells": sum(1 for row in grid for val in row if val == 0)
                    }
                }
                
        except subprocess.TimeoutExpired:
            return {"error": "Timeout lors de l'exécution du solveur (>60s)"}
        except Exception as e:
            return {"error": f"Erreur lors de l'exécution: {str(e)}"}
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)