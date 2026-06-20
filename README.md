# CBUS with Heuristic and Meta heuristic approach

### Constraints

- A passenger's pickup (node `i`, `1 ≤ i ≤ n`) must occur before their drop-off (node `i + n`) in the route.
- At no point may the bus carry more than `k` passengers simultaneously.
- `1 ≤ n ≤ 1000`, `1 ≤ k ≤ 50`
- Time Limit on HUSTACK is 300s, but to be safe in the solution it is set to 250s

## Solution

| File | Approach | Description |
|---|---|---|
| `Greedy.py` | Nearest-neighbor construction | Builds one feasible route greedily, no optimization |
| `LocalSearch.py` | Greedy + 2-opt local search | Greedy solution, then iteratively improved until a local optimum |
| `TabuSearch.py` | Tabu Search | 2-opt solution, then optimized with memory-guided search that escapes local optima |


## 1. Greedy

### Mechanism

From node 0, travel to nearest feasible neighboring node, repeat until 2n stops have been visited

### Properties

- **Time complexity:** O(n²) — Two nested for loop to scan for nearest neighbor for each iteration
- **Limitation:** Greedy may result in overall worse result

### Score on HUSTACK : 474 / 500
---

## 2. Local Search 

### Mechanism

Takes the **Greedy** route as the initial route, and use **2-opt** local search algorithm to improve it until it reaches a local optimum

### Properties

- **Time complexity per iteration:** each full pass is O(n²) for delta evaluation; feasibility checks add O(n) per accepted/attempted swap; run until locally optimal or hitting the time limit
- **Limitation:** gets permanently stuck at the first local optimum reached.

### Score on HUSTACK : 482 / 500
---

## 3. Tabu Search 

### Mechanism

Starts from the **2-opt local search** route and runs a full **Tabu Search**: at every iteration, consider all swap moves, willing to accept the best available move even if it temporarily worsens the route, as long as that move isn't "tabu" (recently reversed). A short-term memory (the tabu list) prevents the search from immediately undoing its own recent moves and fall back into local optimum, allowing the escape of local optima.

### Properties

- **Time complexity per iteration:** O(n²) to scan the full swap neighborhood, with O(n) feasibility checks only on promising candidates (after pruning).
- **Escapes local optima:** unlike Local Search, it can accept a worsening move when it's the best available, allowing it to move past the kind of local optimum that traps the 2-opt approach.
- **Known limitation:** the swap-only neighborhood becomes very restrictive when `k` is small (tight capacity), since most arbitrary two-position swaps violate capacity or precedence — this can cause the neighborhood to be exhausted quickly (no admissible feasible move left), ending the search early ( Test case 1 in HUSTACK )

### Score on HUSTACK : 483 / 500
---