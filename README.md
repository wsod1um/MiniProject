# Project 14 - CBUS Large

**Difficulty:** Hard

A bus-routing problem solved with three progressively more powerful heuristics: **Greedy Construction**, **Local Search (2-opt / swap)**, and **Tabu Search**.

## Problem Statement

There are `n` passengers numbered `1, 2, ..., n`. Passenger `i` wants to travel from point `i` to point `i + n`. A bus starts at point `0` and has capacity `k` (at most `k` passengers on board at any time). Given the distance matrix `c` (where `c[i][j]` is the travel distance from point `i` to point `j`), find the shortest route for the bus that serves all `n` passengers and returns to point `0`.

### Constraints

- A passenger's **pickup** (node `i`, `1 ≤ i ≤ n`) must occur before their **drop-off** (node `i + n`) in the route.
- At no point may the bus carry more than `k` passengers simultaneously.
- `1 ≤ n ≤ 1000`, `1 ≤ k ≤ 50`

### Input Format

```
Line 1:      n k
Line 2..2n+2: the (2n+1) x (2n+1) distance matrix c, one row per line
             (rows/columns indexed 0, 1, ..., 2n)
```

### Output Format

```
Line 1: n
Line 2: the sequence of 2n stops (pickups and drop-offs), space-separated
```

The implicit start/end point `0` is **not** printed — the route is understood to begin and end at the depot.

### Example

**Input**
```
5 3
0 5 8 11 12 8 3 3 7 5 5
5 0 3 5 7 5 3 4 2 2 2
8 3 0 7 8 8 5 7 1 6 5
11 5 7 0 1 5 9 8 6 5 6
12 7 8 1 0 6 10 10 7 7 7
8 5 8 5 6 0 8 5 7 3 4
3 3 5 9 10 8 0 3 4 5 4
3 4 7 8 10 5 3 0 6 2 2
7 2 1 6 7 7 4 6 0 5 4
5 2 6 5 7 3 5 2 5 0 1
5 2 5 6 7 4 4 2 4 1 0
```

**Output**
```
5
1 2 6 7 5 10 3 4 8 9
```

---

## Solution Files

| File | Approach | Description |
|---|---|---|
| `Greedy.py` | Nearest-neighbor construction | Builds one feasible route greedily, no optimization |
| `LocalSearch.py` | Greedy + 2-opt/swap local search | Greedy solution, then iteratively improved until a local optimum |
| `TabuSearch.py` | Greedy + Tabu Search | Greedy solution, then optimized with memory-guided search that escapes local optima |

Each script reads the problem instance from `stdin` and writes the route to `stdout` in the format described above.

```bash
python Greedy.py < input.txt
python LocalSearch.py < input.txt
python TabuSearch.py < input.txt
```

---

## 1. Greedy (`Greedy.py`)

### Mechanism

A pure **nearest-neighbor construction heuristic**. Starting from the depot (node `0`), the bus repeatedly travels to the closest *feasible* unvisited node, until all `2n` stops have been visited.

### Flow

```
route = []
visited = [False] * (2n+1)
load = 0
current_node = 0

repeat 2n times:
    best_next = the unvisited node v minimizing c[current_node][v], subject to:
        - v is a pickup (v <= n) only if load < k
        - v is a drop-off (v > n) only if its matching pickup (v - n) was already visited
    mark best_next visited, move there, append to route
    update load (+1 on pickup, -1 on drop-off)

return route
```

### Properties

- **Time complexity:** O(n²) — for each of the `2n` steps, scan up to `2n` candidate nodes.
- **Always feasible:** every step only considers nodes that satisfy the capacity and precedence constraints, so the resulting route is guaranteed valid.
- **No optimization:** it never reconsiders an earlier decision — a locally cheap edge early on can force expensive edges later. Used purely as the starting point for the other two approaches.

---

## 2. Local Search (`LocalSearch.py`)

### Mechanism

Takes the Greedy route and improves it using a **swap-based local search** (exchanging the positions of two stops in the route, evaluated like a restricted 2-opt move) until no improving swap can be found — i.e., until reaching a **local optimum**.

### Flow

```
route = Greedy(c, n, k)

repeat until no improvement found OR time limit reached:
    for each pair of positions (i, j) in route:
        delta = cost change of swapping route[i] and route[j]   # O(1), via edge deltas only
        if delta < 0:                                            # candidate looks better
            swap route[i], route[j]
            if route is still valid (capacity + precedence):
                accept the swap, restart scanning from the top
            else:
                undo the swap, keep scanning

return route
```

### Key mechanics

- **`calculate_swap`**: computes the cost delta of a swap in O(1) by only looking at the edges adjacent to the two swapped positions, instead of recomputing the entire route cost.
- **`is_valid`**: a full O(n) feasibility re-check (capacity never exceeds `k`, every drop-off occurs after its pickup), run only on candidates with a negative delta.
- **First-improvement strategy**: as soon as *any* improving, feasible swap is found, it's applied immediately and the scan restarts from the beginning — it does not search for the single *best* improving swap.

### Properties

- **Time complexity:** each full pass is O(n²) for delta evaluation; feasibility checks add O(n) per accepted/attempted swap; the algorithm can run many passes until convergence or the time limit.
- **Stopping condition:** terminates once a full pass finds zero improving feasible swaps (a true local optimum) or the time budget (250s) is exhausted.
- **Limitation:** gets permanently stuck at the first local optimum it reaches — it has no mechanism to accept a worse move in order to escape toward a better region of the search space.

---

## 3. Tabu Search (`TabuSearch.py`)

### Mechanism

Starts directly from the **Greedy** route (no separate local-search phase) and runs a full **Tabu Search**: at every iteration it considers *all* swap moves, and — unlike Local Search — is willing to accept the best available move even if it temporarily worsens the route, as long as that move isn't "tabu" (recently reversed). A short-term memory (the tabu list) prevents the search from immediately undoing its own recent moves, which is what allows it to escape local optima that would trap plain Local Search.

### Flow

```
route = Greedy(c, n, k)
current = route, current_cost = total_cost(current)
best = current, best_cost = current_cost
tabu_list = {}                      # move -> iteration it expires
tenure = max(5, n // 10)            # how long a move stays forbidden
no_improve = 0

repeat until time limit reached:

    # --- find the best admissible move in the full neighborhood ---
    best_delta = +infinity
    for each pair of positions (i, j) in current:
        delta = cost change of swapping current[i] and current[j]
        if delta >= best_delta:
            continue                          # not promising enough, skip (prune)

        move = sorted (current[i], current[j])           # order-independent move identity
        is_tabu = move is in tabu_list and still active

        if is_tabu and (current_cost + delta) >= best_cost:
            continue                          # forbidden, and not a new global best -> skip

        tentatively swap, check feasibility (capacity + precedence), undo
        if feasible:
            remember this as the new best candidate (best_delta, best_pair, best_move)

    if no admissible candidate was found:
        stop                                  # neighborhood exhausted

    # --- commit the best candidate found, even if it doesn't improve current_cost ---
    apply best_pair swap to current
    current_cost += best_delta
    mark best_move as tabu until (current_iteration + tenure)
    prune expired entries from tabu_list

    if current_cost < best_cost:
        best, best_cost = current, current_cost
        no_improve = 0
    else:
        no_improve += 1

    # --- diversification: if stuck without improvement, reset to the best-known route ---
    if no_improve > 200:
        current, current_cost = best, best_cost
        no_improve = 0

return best
```

### Key mechanics

| Component | Role |
|---|---|
| **Tabu list** | Maps each recently-made move (an order-independent pair of swapped node IDs) to the iteration after which it becomes legal again. Prevents the search from immediately reversing its own recent moves and cycling. |
| **Tenure** | How many iterations a move stays forbidden (`max(5, n // 10)`). Short tenure risks cycling; long tenure over-restricts the search. |
| **Aspiration criterion** | Overrides the tabu restriction if the forbidden move would produce a new all-time-best solution — ensures the tabu list never blocks a genuinely excellent move. |
| **Best-vs-current tracking** | `current` is allowed to wander into worse territory (that's the point); `best` is tracked completely separately and is what gets returned at the end. |
| **Pruning (`delta >= best_delta: continue`)** | Skips the expensive O(n) feasibility check for any candidate that couldn't possibly become the best move this iteration, regardless of tabu status — keeps each iteration fast. |
| **Stagnation reset** | If 200 consecutive iterations pass with no improvement to `best_cost`, `current` is reset back to `best` to avoid wasting the remaining time budget wandering in an unproductive region. |

### Properties

- **Time complexity per iteration:** O(n²) to scan the full swap neighborhood, with O(n) feasibility checks only on promising candidates (after pruning).
- **Escapes local optima:** unlike Local Search, it can accept a worsening move when it's the best available, allowing it to move past the kind of local optimum that traps the 2-opt approach.
- **Known limitation:** the swap-only neighborhood becomes very restrictive when `k` is small (tight capacity), since most arbitrary two-position swaps violate capacity or precedence — this can cause the neighborhood to be exhausted quickly (no admissible feasible move left), ending the search early. A relocate/insertion move type would broaden the neighborhood for tightly-capacitated instances.

---

## Comparison Summary

| | Greedy | Local Search | Tabu Search |
|---|---|---|---|
| Starting point | — | Greedy route | Greedy route |
| Accepts worsening moves | No | No | Yes (with memory to avoid cycling) |
| Gets stuck at first local optimum | N/A | Yes | No (until neighborhood is exhausted) |
| Tracks best-ever separately | No | No (current = best by construction) | Yes |
| Relative solution quality | Baseline | Better than Greedy | Best, given enough iterations and a rich-enough neighborhood |
| Relative speed | Fastest | Fast | Slower per iteration, but uses the full time budget to keep improving |