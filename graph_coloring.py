"""
Module pour résoudre le problème de coloriage de graphe avec SAT
"""
import tempfile
import subprocess
import os
import io
import base64
from typing import List, Dict, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import matplotlib.pyplot as plt
import networkx as nx


class GraphColoringSAT:
    """Résout le problème de coloriage de graphe en utilisant un solveur SAT"""
    
    def __init__(self, gophersat_path: str):
        self.gophersat_path = gophersat_path
        
    def encode_variable(self, vertex: str, color: str, vertices: List[str], colors: List[str]) -> int:
        """
        Encode une variable (sommet, couleur) en un entier unique
        Variable x_{v,c} : le sommet v a la couleur c
        
        Formule: position_sommet * nb_couleurs + position_couleur + 1
        """
        v_idx = vertices.index(vertex)
        c_idx = colors.index(color)
        return v_idx * len(colors) + c_idx + 1
    
    def decode_variable(self, var_num: int, vertices: List[str], colors: List[str]) -> Tuple[str, str]:
        """Décode un numéro de variable en (sommet, couleur)"""
        var_num -= 1  # Retour à l'indexation 0
        v_idx = var_num // len(colors)
        c_idx = var_num % len(colors)
        return vertices[v_idx], colors[c_idx]
    
    def generate_cnf(self, vertices: List[str], edges: List[Tuple[str, str]], 
                     colors: List[str]) -> Tuple[str, int, int]:
        """
        Génère le fichier CNF pour le problème de coloriage avec commentaires détaillés
        
        Format CNF avec:
        - Commentaires expliquant le graphe et les couleurs
        - Mapping des variables (ex: 1 = A_r, 2 = A_v, etc.)
        - Clauses organisées par type de contrainte
        
        Contraintes:
        1. Chaque sommet doit avoir au moins une couleur
        2. Chaque sommet ne peut avoir qu'une seule couleur (pairwise)
        3. Deux sommets adjacents ne peuvent avoir la même couleur
        
        Returns:
            (cnf_content, nb_variables, nb_clauses)
        """
        clauses = []
        
        # Nombre total de variables: |V| * |K|
        nb_variables = len(vertices) * len(colors)
        
        # En-têtes avec commentaires
        cnf_lines = []
        edges_str = ','.join(['{'+','.join(e)+'}' for e in edges])
        cnf_lines.append(f"c Graph coloring for G = (V,E) with V={{{','.join(vertices)}}}, E={{{edges_str}}}")
        cnf_lines.append(f"c Colors K = {{{','.join(colors)}}}")
        cnf_lines.append("c")
        cnf_lines.append("c Variable mapping:")
        
        # Mapping des variables avec alignement
        var_num = 1
        for vertex in vertices:
            for color in colors:
                cnf_lines.append(f"c {var_num:2d} = {vertex}_{color}")
                var_num += 1
        cnf_lines.append("c")
        
        # Contrainte 1: Chaque sommet doit avoir au moins une couleur
        for vertex in vertices:
            clause = []
            for color in colors:
                var = self.encode_variable(vertex, color, vertices, colors)
                clause.append(var)
            clauses.append(clause)
        
        # Contrainte 2: Chaque sommet ne peut avoir qu'une seule couleur (pairwise)
        for vertex in vertices:
            for i, color1 in enumerate(colors):
                for color2 in colors[i+1:]:
                    var1 = self.encode_variable(vertex, color1, vertices, colors)
                    var2 = self.encode_variable(vertex, color2, vertices, colors)
                    clauses.append([-var1, -var2])
        
        # Contrainte 3: Deux sommets adjacents ne peuvent avoir la même couleur
        for u, v in edges:
            for color in colors:
                var_u = self.encode_variable(u, color, vertices, colors)
                var_v = self.encode_variable(v, color, vertices, colors)
                clauses.append([-var_u, -var_v])
        
        nb_clauses = len(clauses)
        
        # Ligne p cnf
        cnf_lines.append(f"p cnf {nb_variables} {nb_clauses}")
        
        # Ajouter TOUTES les clauses SANS commentaires intermédiaires
        # (GopherSAT n'accepte pas les commentaires après la ligne p cnf)
        for clause in clauses:
            clause_str = " ".join(map(str, clause)) + " 0"
            cnf_lines.append(clause_str)
        
        cnf_content = "\n".join(cnf_lines)
        return cnf_content, nb_variables, nb_clauses
    
    def plot_graph(self, vertices: List[str], edges: List[Tuple[str, str]], 
                   coloring: Dict[str, str]) -> str:
        """
        Génère une visualisation du graphe colorié
        
        Args:
            vertices: Liste des sommets
            edges: Liste des arêtes
            coloring: Dictionnaire {sommet: couleur}
            
        Returns:
            Image encodée en base64
        """
        # Créer le graphe avec NetworkX
        G = nx.Graph()
        G.add_nodes_from(vertices)
        G.add_edges_from(edges)
        
        # Mapper les couleurs abrégées vers des couleurs matplotlib
        color_map = {
            'r': 'red',
            'v': 'green',
            'b': 'blue',
            'rouge': 'red',
            'vert': 'green',
            'bleu': 'blue',
            'green': 'green',
            'jaune': 'yellow',
            'y': 'yellow',
            'orange': 'orange',
            'o': 'orange',
            'violet': 'purple',
            'p': 'purple',
            'rose': 'pink',
            'cyan': 'cyan',
            'c': 'cyan'
        }
        
        # Obtenir les couleurs pour chaque nœud
        node_colors = []
        for node in G.nodes():
            color = coloring.get(node, 'gray')
            # Mapper vers une couleur matplotlib
            matplotlib_color = color_map.get(color.lower(), color)
            node_colors.append(matplotlib_color)
        
        # Créer la figure
        plt.figure(figsize=(10, 8))
        
        # Position des nœuds (layout automatique)
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Dessiner le graphe
        nx.draw(G, pos, 
                node_color=node_colors,
                node_size=1500,
                with_labels=True,
                font_size=16,
                font_weight='bold',
                font_color='white',
                edge_color='gray',
                linewidths=2,
                edgecolors='black')
        
        plt.title("Graphe Colorié", fontsize=18, fontweight='bold')
        
        # Ajouter une légende avec les couleurs utilisées
        unique_colors = set(coloring.values())
        legend_elements = []
        for color in unique_colors:
            matplotlib_color = color_map.get(color.lower(), color)
            legend_elements.append(
                plt.Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor=matplotlib_color, markersize=10,
                          label=f'Couleur: {color}')
            )
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def solve(self, vertices: List[str], edges: List[Tuple[str, str]], 
              colors: List[str]) -> Dict:
        """
        Résout le problème de coloriage de graphe
        
        Prend en entrée les ensembles V, E, K
        Retourne un coloriage φ : V → K s'il existe, sinon None
        
        Args:
            vertices: V - Liste des sommets (ex: ['A', 'B', 'C', 'D'])
            edges: E - Liste des arêtes (ex: [('A', 'B'), ('A', 'C')])
            colors: K - Liste des couleurs (ex: ['r', 'v', 'b'])
            
        Returns:
            Dictionnaire avec:
            - satisfiable: bool
            - phi: Dict[str, str] ou None (le coloriage φ : V → K)
            - cnf_file: str (le fichier CNF généré)
            - stats: Dict (statistiques)
        """
        # Validation
        if not vertices:
            return {"error": "La liste des sommets V est vide"}
        if not colors:
            return {"error": "La liste des couleurs K est vide"}
        
        # Vérifier que les arêtes référencent des sommets existants
        vertex_set = set(vertices)
        for u, v in edges:
            if u not in vertex_set or v not in vertex_set:
                return {"error": f"Arête invalide: ({u}, {v}) - sommets non dans V"}
        
        # Générer le CNF
        try:
            cnf_content, nb_vars, nb_clauses = self.generate_cnf(vertices, edges, colors)
        except Exception as e:
            return {"error": f"Erreur lors de la génération du CNF: {str(e)}"}
        
        # Créer un fichier temporaire avec encodage UTF-8
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False, newline='\n', encoding='utf-8') as temp_file:
            temp_path = temp_file.name
            temp_file.write(cnf_content)
            temp_file.write('\n')  # Ajouter une ligne vide à la fin
            temp_file.flush()  # Forcer l'écriture
        
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
                # Décoder la solution - φ : V → K
                phi = {}  # Le coloriage φ
                for var_str in solution_vars:
                    if var_str != '0':
                        var_num = int(var_str)
                        if var_num > 0:  # Variable vraie
                            vertex, color = self.decode_variable(var_num, vertices, colors)
                            phi[vertex] = color
                
                # Générer la visualisation
                try:
                    plot_image = self.plot_graph(vertices, edges, phi)
                except Exception as e:
                    plot_image = None
                    print(f"Erreur lors de la génération du plot: {e}")
                
                return {
                    "satisfiable": True,
                    "phi": phi,  # φ : V → K (le coloriage)
                    "message": f"Coloriage trouvé: φ : V → K où φ = {phi}",
                    "plot": plot_image,  # Image base64
                    "cnf_file": cnf_content,
                    "stats": {
                        "nb_variables": nb_vars,
                        "nb_clauses": nb_clauses,
                        "nb_vertices": len(vertices),
                        "nb_edges": len(edges),
                        "nb_colors": len(colors),
                        "colors_used": len(set(phi.values()))
                    },
                    "debug_info": {
                        "gophersat_stdout": result.stdout,
                        "gophersat_stderr": result.stderr,
                        "return_code": result.returncode
                    }
                }
            else:
                return {
                    "satisfiable": False,
                    "phi": None,
                    "message": f"Aucun coloriage n'existe pour ce graphe avec K = {{{','.join(colors)}}}",
                    "cnf_file": cnf_content,
                    "stats": {
                        "nb_variables": nb_vars,
                        "nb_clauses": nb_clauses,
                        "nb_vertices": len(vertices),
                        "nb_edges": len(edges),
                        "nb_colors": len(colors)
                    },
                    "debug_info": {
                        "gophersat_stdout": result.stdout,
                        "gophersat_stderr": result.stderr,
                        "return_code": result.returncode,
                        "parsed_status": status
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