"""
Script de test pour déboguer le problème de coloriage
"""
from graph_coloring import GraphColoringSAT

# Configuration
GOPHERSAT_PATH = r"C:\Users\hp\Downloads\gophersat\gophersat.exe"

# Créer le solveur
solver = GraphColoringSAT(GOPHERSAT_PATH)

# Test avec l'exemple qui fonctionne dans /solve
vertices = ["A", "B", "C", "D"]
edges = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"), ("C", "D")]
colors = ["r", "v", "b"]

print("=" * 60)
print("Test de coloriage de graphe")
print("=" * 60)
print(f"V = {vertices}")
print(f"E = {edges}")
print(f"K = {colors}")
print()

# Générer et afficher le CNF
cnf_content, nb_vars, nb_clauses = solver.generate_cnf(vertices, edges, colors)
print("CNF généré:")
print(cnf_content)
print()
print("=" * 60)

# Résoudre
result = solver.solve(vertices, edges, colors)
print("Résultat:")
print(result)