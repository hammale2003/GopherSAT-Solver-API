"""
Simulateur pour le Sokorridor
Permet de visualiser et vérifier l'exécution d'un plan
"""
from typing import List, Dict, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from PIL import Image


class SokobanSimulator:
    """Simule l'exécution d'un plan Sokorridor"""
    
    def __init__(self, num_cells: int = 11):
        self.num_cells = num_cells
        self.reset()
    
    def reset(self):
        """Réinitialise l'état"""
        self.worker_pos = 0
        self.boxes = []
        self.goals = []
        self.walls = [0, self.num_cells - 1]  # Murs aux extrémités
        self.history = []
    
    def set_initial_state(self, worker_pos: int, boxes: List[int], goals: List[int]):
        """Définit l'état initial"""
        self.worker_pos = worker_pos
        self.boxes = boxes.copy()
        self.goals = goals
        self.history = [self.get_state()]
    
    def get_state(self) -> Dict:
        """Retourne l'état actuel"""
        return {
            'worker': self.worker_pos,
            'boxes': self.boxes.copy()
        }
    
    def is_valid_position(self, pos: int) -> bool:
        """Vérifie si une position est valide"""
        return 0 < pos < self.num_cells - 1
    
    def is_goal_reached(self) -> bool:
        """Vérifie si tous les objectifs sont atteints"""
        return set(self.boxes) == set(self.goals)
    
    def execute_action(self, action: str) -> Tuple[bool, str]:
        """
        Exécute une action
        
        Returns:
            (success, message)
        """
        if action == 'move_right':
            return self.move_right()
        elif action == 'move_left':
            return self.move_left()
        elif action == 'push_right':
            return self.push_right()
        elif action == 'push_left':
            return self.push_left()
        else:
            return False, f"Action inconnue: {action}"
    
    def move_right(self) -> Tuple[bool, str]:
        """Déplacer le worker à droite"""
        new_pos = self.worker_pos + 1
        
        if not self.is_valid_position(new_pos):
            return False, "Mur à droite"
        
        if new_pos in self.boxes:
            return False, "Caisse bloque le passage"
        
        self.worker_pos = new_pos
        self.history.append(self.get_state())
        return True, "Déplacé à droite"
    
    def move_left(self) -> Tuple[bool, str]:
        """Déplacer le worker à gauche"""
        new_pos = self.worker_pos - 1
        
        if not self.is_valid_position(new_pos):
            return False, "Mur à gauche"
        
        if new_pos in self.boxes:
            return False, "Caisse bloque le passage"
        
        self.worker_pos = new_pos
        self.history.append(self.get_state())
        return True, "Déplacé à gauche"
    
    def push_right(self) -> Tuple[bool, str]:
        """Pousser une caisse à droite"""
        box_pos = self.worker_pos + 1
        new_box_pos = self.worker_pos + 2
        
        if not self.is_valid_position(box_pos):
            return False, "Pas de case à droite"
        
        if box_pos not in self.boxes:
            return False, "Pas de caisse à pousser"
        
        if not self.is_valid_position(new_box_pos):
            return False, "Mur bloque la caisse"
        
        if new_box_pos in self.boxes:
            return False, "Une autre caisse bloque"
        
        # Déplacer la caisse
        self.boxes.remove(box_pos)
        self.boxes.append(new_box_pos)
        
        # Déplacer le worker
        self.worker_pos = box_pos
        
        self.history.append(self.get_state())
        return True, "Caisse poussée à droite"
    
    def push_left(self) -> Tuple[bool, str]:
        """Pousser une caisse à gauche"""
        box_pos = self.worker_pos - 1
        new_box_pos = self.worker_pos - 2
        
        if not self.is_valid_position(box_pos):
            return False, "Pas de case à gauche"
        
        if box_pos not in self.boxes:
            return False, "Pas de caisse à pousser"
        
        if not self.is_valid_position(new_box_pos):
            return False, "Mur bloque la caisse"
        
        if new_box_pos in self.boxes:
            return False, "Une autre caisse bloque"
        
        # Déplacer la caisse
        self.boxes.remove(box_pos)
        self.boxes.append(new_box_pos)
        
        # Déplacer le worker
        self.worker_pos = box_pos
        
        self.history.append(self.get_state())
        return True, "Caisse poussée à gauche"
    
    def execute_plan(self, plan: List[Tuple[int, str]]) -> Dict:
        """
        Exécute un plan complet
        
        Args:
            plan: Liste de (time, action)
            
        Returns:
            Résultat de l'exécution
        """
        results = []
        
        for time, action in plan:
            success, message = self.execute_action(action)
            results.append({
                'time': time,
                'action': action,
                'success': success,
                'message': message,
                'state': self.get_state()
            })
            
            if not success:
                return {
                    'success': False,
                    'message': f"Échec à l'étape {time}: {message}",
                    'steps': results,
                    'goal_reached': False
                }
        
        goal_reached = self.is_goal_reached()
        
        return {
            'success': True,
            'message': "Plan exécuté avec succès" if goal_reached else "Plan exécuté mais objectif non atteint",
            'steps': results,
            'goal_reached': goal_reached,
            'history': self.history
        }
    
    def render_state(self, state: Dict = None, title: str = "") -> str:
        """Génère une représentation ASCII de l'état"""
        if state is None:
            state = self.get_state()
        
        # Créer la ligne de représentation
        line = ['#']  # Mur gauche
        
        for pos in range(1, self.num_cells - 1):
            if pos == state['worker']:
                if pos in self.goals:
                    line.append('+')  # Worker sur objectif
                else:
                    line.append('@')
            elif pos in state['boxes']:
                if pos in self.goals:
                    line.append('*')  # Caisse sur objectif
                else:
                    line.append('$')
            elif pos in self.goals:
                line.append('.')
            else:
                line.append(' ')
        
        line.append('#')  # Mur droit
        
        result = ''.join(line)
        if title:
            result = f"{title}\n{result}"
        return result
    
    def visualize(self, state: Dict = None, title: str = "") -> str:
        """
        Génère une visualisation graphique de l'état
        
        Returns:
            Image encodée en base64
        """
        if state is None:
            state = self.get_state()
        
        fig, ax = plt.subplots(figsize=(12, 2))
        
        # Configuration
        cell_size = 1
        ax.set_xlim(-0.5, self.num_cells - 0.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Dessiner les cases
        for pos in range(self.num_cells):
            # Fond
            if pos in self.goals:
                color = 'lightgreen'
            elif pos in self.walls:
                color = 'gray'
            else:
                color = 'white'
            
            rect = patches.Rectangle((pos - 0.4, 0.1), 0.8, 0.8,
                                     linewidth=2, edgecolor='black',
                                     facecolor=color)
            ax.add_patch(rect)
            
            # Contenu
            if pos == state['worker']:
                # Worker (personnage)
                circle = patches.Circle((pos, 0.5), 0.3, color='blue')
                ax.add_patch(circle)
                ax.text(pos, 0.5, '@', ha='center', va='center',
                       fontsize=16, fontweight='bold', color='white')
            
            if pos in state['boxes']:
                # Caisse
                box_rect = patches.Rectangle((pos - 0.25, 0.25), 0.5, 0.5,
                                            linewidth=2, edgecolor='brown',
                                            facecolor='orange')
                ax.add_patch(box_rect)
                ax.text(pos, 0.5, '$', ha='center', va='center',
                       fontsize=14, fontweight='bold', color='brown')
            
            # Numéros de cases
            ax.text(pos, -0.2, str(pos), ha='center', va='center',
                   fontsize=10, color='gray')
        
        # Légende
        legend_y = 1.2
        ax.text(0, legend_y, '@ = Worker', fontsize=10)
        ax.text(3, legend_y, '$ = Caisse', fontsize=10)
        ax.text(6, legend_y, '░ = Objectif', fontsize=10, 
               bbox=dict(boxstyle='round', facecolor='lightgreen'))
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def visualize_plan_execution(self, plan_result: Dict) -> List[str]:
        """
        Génère une série d'images montrant l'exécution du plan
        
        Returns:
            Liste d'images base64
        """
        images = []
        
        # État initial
        images.append(self.visualize(self.history[0], "État Initial"))
        
        # Chaque étape
        for i, step in enumerate(plan_result['steps']):
            title = f"Étape {step['time']}: {step['action']} - {step['message']}"
            images.append(self.visualize(step['state'], title))
        
        return images
    
    def create_animated_gif(self, plan_result: Dict, duration: int = 500) -> str:
        """
        Crée un GIF animé de l'exécution du plan
        
        Args:
            plan_result: Résultat de l'exécution du plan
            duration: Durée de chaque frame en millisecondes
            
        Returns:
            GIF encodé en base64
        """
        # Générer toutes les images
        pil_images = []
        
        # État initial
        img_b64 = self.visualize(self.history[0], "État Initial")
        img_data = base64.b64decode(img_b64)
        pil_images.append(Image.open(io.BytesIO(img_data)))
        
        # Chaque étape
        for i, step in enumerate(plan_result['steps']):
            action_symbols = {
                'move_right': '→',
                'move_left': '←',
                'push_right': '⇒',
                'push_left': '⇐'
            }
            action_sym = action_symbols.get(step['action'], step['action'])
            title = f"t={step['time']}: {action_sym}"
            
            img_b64 = self.visualize(step['state'], title)
            img_data = base64.b64decode(img_b64)
            pil_images.append(Image.open(io.BytesIO(img_data)))
        
        # Créer le GIF
        gif_buffer = io.BytesIO()
        pil_images[0].save(
            gif_buffer,
            format='GIF',
            save_all=True,
            append_images=pil_images[1:],
            duration=duration,
            loop=0  # Loop infiniment
        )
        gif_buffer.seek(0)
        
        # Encoder en base64
        gif_base64 = base64.b64encode(gif_buffer.read()).decode('utf-8')
        
        return gif_base64