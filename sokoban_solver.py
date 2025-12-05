"""
Sokoban SAT Solver - VERSION FINALE
Encodage simple : chaque action définit complètement l'état suivant
"""
import tempfile
import subprocess
import os
from typing import List, Dict, Tuple
from itertools import combinations


class SokobanSAT:
    def __init__(self, gophersat_path: str):
        self.gophersat_path = gophersat_path
        
    def var(self, name: str, pos: int, time: int, T: int, C: int) -> int:
        """Encodage des variables"""
        if name == 'w':  # worker_position_time
            return time * C + pos + 1
        elif name == 'b':  # box_position_time
            return (T + 1) * C + time * C + pos + 1
        else:  # action_time
            actions = {'mr': 0, 'ml': 1, 'pr': 2, 'pl': 3}
            return 2 * (T + 1) * C + time * 4 + actions[name] + 1
    
    def generate_cnf(self, initial: Dict, goals: List[int], T: int, C: int) -> Tuple[str, int, int]:
        """Génère le CNF"""
        clauses = []
        nb_vars = 2 * (T + 1) * C + T * 4
        
        # État initial
        clauses.append([self.var('w', initial['worker'], 0, T, C)])
        for b in initial['boxes']:
            clauses.append([self.var('b', b, 0, T, C)])
        for c in range(C):
            if c not in initial['boxes']:
                clauses.append([-self.var('b', c, 0, T, C)])
        
        # But
        for g in goals:
            clauses.append([self.var('b', g, T, T, C)])
        
        # Worker : exactement une case
        for t in range(T + 1):
            clauses.append([self.var('w', c, t, T, C) for c in range(C)])
            for c1 in range(C):
                for c2 in range(c1 + 1, C):
                    clauses.append([-self.var('w', c1, t, T, C), -self.var('w', c2, t, T, C)])
        
        # Action : exactement une par temps
        for t in range(T):
            clauses.append([self.var(a, 0, t, T, C) for a in ['mr', 'ml', 'pr', 'pl']])
            for a1, a2 in combinations(['mr', 'ml', 'pr', 'pl'], 2):
                clauses.append([-self.var(a1, 0, t, T, C), -self.var(a2, 0, t, T, C)])
        
        # Transitions
        for t in range(T):
            for c in range(C):  # TOUTES les positions sont valides (0 à 10)
                w = self.var('w', c, t, T, C)
                
                # Interdire les actions impossibles aux bords
                pr = self.var('pr', 0, t, T, C)
                pl = self.var('pl', 0, t, T, C)
                
                # Si worker en position où push_right est impossible, interdire push_right
                if c + 2 >= C:
                    clauses.append([-w, -pr])  # worker_c ∧ push_right est IMPOSSIBLE
                
                # Si worker en position où push_left est impossible, interdire push_left
                if c - 2 < 0:
                    clauses.append([-w, -pl])  # worker_c ∧ push_left est IMPOSSIBLE
                
                # MOVE RIGHT
                if c + 1 < C:
                    mr = self.var('mr', 0, t, T, C)
                    b_next = self.var('b', c + 1, t, T, C)
                    w_next = self.var('w', c + 1, t + 1, T, C)
                    
                    clauses.append([-w, -mr, -b_next])  # Précondition
                    clauses.append([-w, -mr, w_next])    # Effet sur worker
                    
                    # Les boxes ne changent PAS
                    for bc in range(C):
                        b_t = self.var('b', bc, t, T, C)
                        b_t1 = self.var('b', bc, t + 1, T, C)
                        clauses.append([-w, -mr, -b_t, b_t1])
                        clauses.append([-w, -mr, b_t, -b_t1])
                
                # MOVE LEFT
                if c - 1 >= 0:
                    ml = self.var('ml', 0, t, T, C)
                    b_prev = self.var('b', c - 1, t, T, C)
                    w_prev = self.var('w', c - 1, t + 1, T, C)
                    
                    clauses.append([-w, -ml, -b_prev])
                    clauses.append([-w, -ml, w_prev])
                    
                    for bc in range(C):
                        b_t = self.var('b', bc, t, T, C)
                        b_t1 = self.var('b', bc, t + 1, T, C)
                        clauses.append([-w, -ml, -b_t, b_t1])
                        clauses.append([-w, -ml, b_t, -b_t1])
                
                # PUSH RIGHT
                if c + 2 < C:
                    pr = self.var('pr', 0, t, T, C)
                    b_c1_t = self.var('b', c + 1, t, T, C)
                    b_c2_t = self.var('b', c + 2, t, T, C)
                    w_c1_t1 = self.var('w', c + 1, t + 1, T, C)
                    b_c1_t1 = self.var('b', c + 1, t + 1, T, C)
                    b_c2_t1 = self.var('b', c + 2, t + 1, T, C)
                    
                    # Préconditions
                    clauses.append([-w, -pr, b_c1_t])
                    clauses.append([-w, -pr, -b_c2_t])
                    
                    # Effets
                    clauses.append([-w, -pr, w_c1_t1])
                    clauses.append([-w, -pr, -b_c1_t1])
                    clauses.append([-w, -pr, b_c2_t1])
                    
                    # Autres boxes ne changent pas
                    for bc in range(C):
                        if bc != c + 1 and bc != c + 2:
                            b_t = self.var('b', bc, t, T, C)
                            b_t1 = self.var('b', bc, t + 1, T, C)
                            clauses.append([-w, -pr, -b_t, b_t1])
                            clauses.append([-w, -pr, b_t, -b_t1])
                
                # PUSH LEFT
                if c - 2 >= 0:
                    pl = self.var('pl', 0, t, T, C)
                    b_cm1_t = self.var('b', c - 1, t, T, C)
                    b_cm2_t = self.var('b', c - 2, t, T, C)
                    w_cm1_t1 = self.var('w', c - 1, t + 1, T, C)
                    b_cm1_t1 = self.var('b', c - 1, t + 1, T, C)
                    b_cm2_t1 = self.var('b', c - 2, t + 1, T, C)
                    
                    clauses.append([-w, -pl, b_cm1_t])
                    clauses.append([-w, -pl, -b_cm2_t])
                    clauses.append([-w, -pl, w_cm1_t1])
                    clauses.append([-w, -pl, -b_cm1_t1])
                    clauses.append([-w, -pl, b_cm2_t1])
                    
                    for bc in range(C):
                        if bc != c - 1 and bc != c - 2:
                            b_t = self.var('b', bc, t, T, C)
                            b_t1 = self.var('b', bc, t + 1, T, C)
                            clauses.append([-w, -pl, -b_t, b_t1])
                            clauses.append([-w, -pl, b_t, -b_t1])
        
        # Génération CNF
        lines = [f"c Sokoban SAT", f"p cnf {nb_vars} {len(clauses)}"]
        for clause in clauses:
            lines.append(" ".join(map(str, clause)) + " 0")
        
        return "\n".join(lines), nb_vars, len(clauses)
    
    def solve(self, initial_state: Dict, goals: List[int], T: int = 15, num_cells: int = 11) -> Dict:
        """Résout le Sokoban"""
        try:
            cnf, V, C_count = self.generate_cnf(initial_state, goals, T, num_cells)
        except Exception as e:
            return {"error": str(e)}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cnf', delete=False, newline='\n', encoding='utf-8') as f:
            f.write(cnf + '\n')
            temp_path = f.name
        
        try:
            result = subprocess.run([self.gophersat_path, temp_path], capture_output=True, text=True, timeout=60)
            
            status = None
            vars_list = []
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('s '):
                    status = line[2:].strip()
                elif line.startswith('v '):
                    vars_list.extend(line[2:].strip().split())
            
            if status == "SATISFIABLE":
                plan = []
                action_map = {0: 'move_right', 1: 'move_left', 2: 'push_right', 3: 'push_left'}
                offset = 2 * (T + 1) * num_cells
                
                for var_str in vars_list:
                    if var_str and var_str != '0':
                        var_num = int(var_str)
                        if var_num > offset:
                            idx = var_num - offset - 1
                            time = idx // 4
                            action_idx = idx % 4
                            if time < T:
                                plan.append((time, action_map[action_idx]))
                
                plan.sort()
                
                return {
                    "satisfiable": True,
                    "plan": plan,
                    "message": f"Plan en {len(plan)} étapes",
                    "stats": {"nb_variables": V, "nb_clauses": C_count, "horizon": T, "num_cells": num_cells, "plan_length": len(plan)}
                }
            else:
                return {
                    "satisfiable": False,
                    "message": f"Pas de solution avec T={T}",
                    "stats": {"nb_variables": V, "nb_clauses": C_count, "horizon": T, "num_cells": num_cells}
                }
        except Exception as e:
            return {"error": str(e)}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)