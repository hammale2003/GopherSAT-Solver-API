## Formalisation du problème

Soit les propositions logiques suivantes :
- `P` : il pleut
- `A` : mon arroseur s'est déclenché  
- `M` : ma pelouse est mouillée

### Règles données :
- **R1** : `P → M` (si il pleut alors ma pelouse est mouillée)
- **R2** : `A → M` (si mon arroseur s'est déclenché alors ma pelouse est mouillée)

---

## Question 1 : Lundi - Déduction

**Contexte** : *Lundi*, il pleut. Que puis-je en déduire ? Formaliser.

### Formalisation :
- **Prémisse** : `P` (il pleut)
- **Règle** : `P → M` (R1)
- **Application du Modus Ponens** : De `P` et `P → M`, on déduit `M`

### Conclusion :
**Je peux déduire que ma pelouse est mouillée (M).**

Cette déduction est **correcte** et **complète** car elle suit logiquement les règles données.

---

## Question 2 : Mardi - Abduction

**Contexte** : *Mardi*, la pelouse est mouillée. Que puis-je abduire ? Ai-je raison ?

### Formalisation :
- **Observation** : `M` (la pelouse est mouillée)
- **Règles disponibles** : 
  - `P → M` (R1)
  - `A → M` (R2)

### Abduction possible :
À partir de `M` et des règles `P → M` et `A → M`, je peux abduire :
1. **Hypothèse 1** : `P` (il a plu)
2. **Hypothèse 2** : `A` (l'arroseur s'est déclenché)
3. **Hypothèse 3** : `P ∧ A` (il a plu ET l'arroseur s'est déclenché)

### Ai-je raison ?
**Non, je n'ai pas forcément raison.** L'abduction n'est pas logiquement valide comme la déduction :
- L'abduction propose des **explications plausibles** mais non garanties
- Il pourrait y avoir d'autres causes non modélisées (ex: le voisin a arrosé ma pelouse)
- L'abduction est **incomplète** : elle ne peut pas déterminer avec certitude la cause réelle

---

## Question 3 : Planification Conformante

**Contexte** : Mercredi, je veux que la pelouse soit mouillée. Comment faire ?

### Objectif :
Garantir `M` (pelouse mouillée) dans un environnement incertain.

### Stratégies possibles :

#### Stratégie 1 : Action contrôlable
- **Action** : Déclencher mon arroseur (`A`)
- **Justification** : `A → M`, donc si j'active `A`, j'obtiens `M`
- **Avantage** : Action sous mon contrôle, résultat garanti

#### Stratégie 2 : Attendre les conditions naturelles
- **Condition** : Espérer qu'il pleuve (`P`)
- **Justification** : `P → M`, donc si `P` alors `M`
- **Inconvénient** : Pas de contrôle sur `P`, résultat incertain

#### Stratégie 3 : Planification robuste
- **Plan** : Vérifier la météo, et si pas de pluie prévue, alors activer l'arroseur
- **Formalisation** :
  ```
  SI (¬P prévu) ALORS A
  ```
- **Avantage** : Économise l'eau si la nature se charge de l'arrosage

### Conclusion :
La **stratégie 1** (déclencher l'arroseur) est la plus sûre pour garantir l'objectif dans un environnement incertain, car elle ne dépend que d'actions contrôlables.

---

---

## Logique des Pénalités - Table de Vérité Complète

### Règles avec pénalités :
- **r₁** : `pluie → ma_pelouse_mouillée`, pénalité = 13
- **r₂** : `pluie → pelouse_voisin_mouillée`, pénalité = 15  
- **r₃** : `mon_arrosage → ma_pelouse_mouillée`, pénalité = 8
- **r₄** : `pelouse_voisin_mouillée → pluie`, pénalité = 6

### Méthode de calcul :
Une règle `A → B` est **violée** (F) si et seulement si `A` est vrai ET `B` est faux.
Le **karma pondéré** = somme des pénalités des règles violées (avec signe négatif).

### Table de vérité complète :

| p | a | m | v | r₁ | r₂ | r₃ | r₄ | karma pondéré | karma anonyme |
|---|---|---|---|----|----|----|----|---------------|---------------|
| 0 | 0 | 0 | 0 | V  | V  | V  | V  | 0             | 0             |
| 0 | 0 | 0 | 1 | V  | V  | V  | F  | -6            | -1            |
| 0 | 0 | 1 | 0 | V  | V  | V  | V  | 0             | 0             |
| 0 | 0 | 1 | 1 | V  | V  | V  | F  | -6            | -1            |
| 0 | 1 | 0 | 0 | V  | V  | F  | V  | -8            | -1            |
| 0 | 1 | 0 | 1 | V  | V  | F  | F  | -14           | -2            |
| 0 | 1 | 1 | 0 | V  | V  | V  | V  | 0             | 0             |
| 0 | 1 | 1 | 1 | V  | V  | V  | F  | -6            | -1            |
| 1 | 0 | 0 | 0 | F  | F  | V  | V  | -28           | -2            |
| 1 | 0 | 0 | 1 | F  | V  | V  | V  | -13           | -1            |
| 1 | 0 | 1 | 0 | V  | F  | V  | V  | -15           | -1            |
| 1 | 0 | 1 | 1 | V  | V  | V  | V  | 0             | 0             |
| 1 | 1 | 0 | 0 | F  | F  | F  | V  | -36           | -3            |
| 1 | 1 | 0 | 1 | F  | V  | F  | V  | -21           | -2            |
| 1 | 1 | 1 | 0 | V  | F  | V  | V  | -15           | -1            |
| 1 | 1 | 1 | 1 | V  | V  | V  | V  | 0             | 0             |

### Analyse des résultats :

**Interprétations optimales (karma = 0) :**
- `p=0, a=0, m=0, v=0` : Rien ne se passe
- `p=0, a=0, m=1, v=0` : Pelouse mouillée sans cause connue
- `p=0, a=1, m=1, v=0` : Arrosage réussi, pas de pluie
- `p=1, a=0, m=1, v=1` : Pluie cohérente avec les deux pelouses mouillées
- `p=1, a=1, m=1, v=1` : Pluie + arrosage, tout cohérent

**Pire interprétation (karma = -36) :**
- `p=1, a=1, m=0, v=0` : Il pleut ET j'arrose, mais aucune pelouse n'est mouillée (viole 3 règles)

---

## Questions Avancées sur la Logique des Pénalités

### 3. Règles Anonymes - Karma Anonyme

**Question** : En supposant que toutes les règles sont pondérées de la même manière (pénalité = 1), comment qualifier les lignes de la table du karma de plus petite valeur ?

**Réponse** :

Le **karma anonyme** compte simplement le nombre de règles violées (toutes les pénalités = 1).

**Interprétations optimales** (karma anonyme = 0) :
- Aucune règle violée, représentent les **modèles cohérents** du système logique
- Ces lignes correspondent aux **solutions satisfaisantes** en logique propositionnelle

**Interprétations de karma anonyme minimal** :
- Karma = -1 : Une seule règle violée (8 interprétations)
- Karma = -2 : Deux règles violées (3 interprétations)  
- Karma = -3 : Trois règles violées (1 interprétation - la pire)

**Qualification** : Les lignes de karma anonyme minimal correspondent aux **explications les plus parcimonieuses** (principe du rasoir d'Ockham en IA).

### 4. Règles Indépendantes

**a) Quel nom donne-t-on parfois à cette hypothèse ?**

Cette hypothèse s'appelle l'**hypothèse d'indépendance naïve** ou **hypothèse de Bayes naïf**.

**b) Quelle relation entretiennent les pénalités et les nombres $p_i$ ?**

Si $p_i$ est la probabilité que la règle $r_i$ soit respectée, alors :

$$\text{pénalité}_i = -\log(p_i)$$

ou plus généralement :

$$\text{pénalité}_i = -\log(1 - \text{prob\_violation}_i)$$

Cette relation transforme les probabilités multiplicatives en pénalités additives, permettant le calcul de vraisemblance par sommation.

### 5. Bornes de Fréchet

**a) Quel encadrement peut-on donner pour $p(A \cup B)$ et $p(A \cap B)$ ?**

**Pour l'union** :
$$\max(p(A), p(B)) \leq p(A \cup B) \leq \min(1, p(A) + p(B))$$

**Pour l'intersection** :
$$\max(0, p(A) + p(B) - 1) \leq p(A \cap B) \leq \min(p(A), p(B))$$

**b) En déduire d'autres façons de calculer le karma de chaque interprétation.**

**Méthode 1 - Bornes pessimistes** :
- Karma minimal = somme des pénalités si toutes les règles en conflit sont violées
- Karma maximal = 0 si aucune règle n'est violée

**Méthode 2 - Probabilités conditionnelles** :
$$P(\text{interprétation}) = \prod_{i} P(r_i \text{ respectée | contexte})$$

Le karma devient : $-\sum_i \log(P(r_i \text{ respectée | contexte}))$

**c) Comment mettre en œuvre ce raisonnement de manière automatique ?**

**Algorithme SAT avec optimisation** :
1. Encoder les règles comme clauses SAT pondérées (Weighted MAX-SAT)
2. Utiliser un solveur SAT pour trouver l'interprétation de coût minimal
3. Énumérer les k-meilleures solutions pour l'abduction

**Algorithme de recherche locale** :
```python
def automated_penalty_reasoning(rules, observations, k_best=5):
    """Raisonnement automatique par logique des pénalités"""
    
    # 1. Générer toutes les interprétations possibles
    interpretations = generate_all_interpretations(variables)
    
    # 2. Calculer le karma de chaque interprétation
    scored_interpretations = []
    for interp in interpretations:
        karma = evaluate_karma(interp, rules)
        scored_interpretations.append((karma, interp))
    
    # 3. Trier par karma croissant (meilleur karma = plus proche de 0)
    scored_interpretations.sort(key=lambda x: x[0], reverse=True)
    
    # 4. Filtrer selon les observations
    compatible_interpretations = []
    for karma, interp in scored_interpretations:
        if is_compatible(interp, observations):
            compatible_interpretations.append((karma, interp))
    
    # 5. Retourner les k meilleures explications
    return compatible_interpretations[:k_best]

def is_compatible(interpretation, observations):
    """Vérifie si une interprétation est compatible avec les observations"""
    for var, value in observations.items():
        if interpretation[var] != value:
            return False
    return True
```

**Optimisations avancées** :
- **Branch & Bound** : Élagage des branches de karma trop élevé
- **A*** : Heuristique basée sur le nombre minimal de règles à violer
- **SAT-Solving** : Transformation en problème de satisfiabilité pondérée

---

## Code Logic (Pseudo-code)

```python
def deduction(premises, rules):
    """Déduction logique : conclusions à partir de prémisses et règles"""
    conclusions = set(premises)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.antecedent.issubset(conclusions) and rule.consequent not in conclusions:
                conclusions.add(rule.consequent)
                changed = True
    return conclusions

def abduction(observations, rules):
    """Abduction : hypothèses plausibles pour expliquer les observations"""
    hypotheses = []
    for rule in rules:
        if rule.consequent in observations:
            hypotheses.append(rule.antecedent)
    return hypotheses

def planning_conformant(goal, rules, controllable_actions):
    """Planification conformante pour atteindre un objectif"""
    plans = []
    for action in controllable_actions:
        for rule in rules:
            if action in rule.antecedent and goal in rule.consequent:
                plans.append(action)
    return plans

def evaluate_karma(interpretation, rules_with_penalties):
    """Évalue le karma pondéré et anonyme d'une interprétation"""
    karma_weighted = 0
    karma_anonymous = 0
    p, a, m, v = interpretation
    
    # Vérifier chaque règle
    rules = [
        (p, m, 13),  # r1: pluie → ma_pelouse_mouillée
        (p, v, 15),  # r2: pluie → pelouse_voisin_mouillée  
        (a, m, 8),   # r3: mon_arrosage → ma_pelouse_mouillée
        (v, p, 6)    # r4: pelouse_voisin_mouillée → pluie
    ]
    
    for antecedent, consequent, penalty in rules:
        if antecedent and not consequent:  # Règle violée
            karma_weighted -= penalty
            karma_anonymous -= 1  # Pénalité anonyme = 1
            
    return karma_weighted, karma_anonymous

def generate_truth_table_complete():
    """Génère la table de vérité complète avec karma pondéré et anonyme"""
    table = []
    for p in [0, 1]:
        for a in [0, 1]:
            for m in [0, 1]:
                for v in [0, 1]:
                    interpretation = (p, a, m, v)
                    karma_w, karma_a = evaluate_karma(interpretation, None)
                    table.append((*interpretation, karma_w, karma_a))
    return table

def automated_penalty_reasoning(rules, observations, k_best=5):
    """Raisonnement automatique par logique des pénalités"""
    
    # 1. Générer toutes les interprétations possibles
    interpretations = generate_all_interpretations(variables)
    
    # 2. Calculer le karma de chaque interprétation
    scored_interpretations = []
    for interp in interpretations:
        karma_w, karma_a = evaluate_karma(interp, rules)
        scored_interpretations.append((karma_w, karma_a, interp))
    
    # 3. Trier par karma croissant (meilleur karma = plus proche de 0)
    scored_interpretations.sort(key=lambda x: (x[0], x[1]), reverse=True)
    
    # 4. Filtrer selon les observations
    compatible_interpretations = []
    for karma_w, karma_a, interp in scored_interpretations:
        if is_compatible(interp, observations):
            compatible_interpretations.append((karma_w, karma_a, interp))
    
    # 5. Retourner les k meilleures explications
    return compatible_interpretations[:k_best]

def is_compatible(interpretation, observations):
    """Vérifie si une interprétation est compatible avec les observations"""
    for var, value in observations.items():
        if interpretation[var] != value:
            return False
    return True

# Exemple d'utilisation
rules = [
    Rule(antecedent={'P'}, consequent={'M'}),  # P → M
    Rule(antecedent={'A'}, consequent={'M'})   # A → M
]

# Question 1 : Déduction
lundi_premises = {'P'}
lundi_conclusions = deduction(lundi_premises, rules)
print(f"Lundi conclusions: {lundi_conclusions}")  # {'P', 'M'}

# Question 2 : Abduction  
mardi_observations = {'M'}
mardi_hypotheses = abduction(mardi_observations, rules)
print(f"Mardi hypothèses: {mardi_hypotheses}")  # [{'P'}, {'A'}]

# Question 3 : Planification
mercredi_goal = {'M'}
controllable = ['A']  # Je peux contrôler l'arroseur
mercredi_plan = planning_conformant(mercredi_goal, rules, controllable)
print(f"Mercredi plan: {mercredi_plan}")  # ['A']

# Logique des pénalités
truth_table = generate_truth_table_complete()
print("Table de vérité avec karma pondéré et anonyme:")
for row in truth_table:
    print(f"p={row[0]}, a={row[1]}, m={row[2]}, v={row[3]} → karma_pondéré={row[4]}, karma_anonyme={row[5]}")

# Exemple d'abduction automatique
observations = {'m': 1, 'v': 0}  # Vendredi: ma pelouse mouillée, voisin non
best_explanations = automated_penalty_reasoning(rules, observations, k_best=3)
print(f"\nMeilleures explications pour le Vendredi: {best_explanations}")
```

### Interprétation pour le Vendredi et Samedi :

**Vendredi** : `ma_pelouse=1, pelouse_voisin=0` (lignes où m=1, v=0)
- Meilleures explications : lignes avec karma=0 ou karma=-15
- `p=0, a=0, m=1, v=0` (karma=0) : pelouse mouillée sans cause connue
- `p=0, a=1, m=1, v=0` (karma=0) : j'ai arrosé ma pelouse

**Samedi** : `ma_pelouse=0, pelouse_voisin=1` (lignes où m=0, v=1)  
- Meilleures explications : ligne avec karma=-6
- `p=0, a=0, m=0, v=1` (karma=-6) : pelouse voisin mouillée, cause inconnue
- Cela viole seulement r₄ (pelouse_voisin → pluie)