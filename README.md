# Project 14 – CBUS Large

## Problem Statement

There are **n** passengers numbered 1 to n. Passenger *i* wishes to travel from
point *i* (pickup) to point *i + n* (drop-off). A single bus departs from
point **0**, may carry at most **k** passengers simultaneously, must serve all
passengers, and must return to point **0**. The goal is to find the
**shortest possible route** for the bus.

---

## Mathematical Model

### Sets and Parameters

| Symbol | Meaning |
|--------|---------|
| n | number of passengers |
| k | bus capacity (maximum simultaneous passengers) |
| N = 2n | total number of stops (n pickups + n drop-offs) |
| c\[i\]\[j\] | travel distance from point i to point j (i, j ∈ {0, 1, …, 2n}) |
| Point 0 | depot – the bus starts and ends here |
| Point i (1 ≤ i ≤ n) | pickup location for passenger i |
| Point i+n (1 ≤ i ≤ n) | drop-off location for passenger i |

### Decision Variable

A route is represented as a **permutation** π = (π₁, π₂, …, π_{2n}) of the
set {1, 2, …, 2n}, describing the order in which the bus visits all stops.

### Objective Function

Minimize the total travel distance:

$$\text{Cost}(\pi) = c[0][\pi_1] + \sum_{t=1}^{2n-1} c[\pi_t][\pi_{t+1}] + c[\pi_{2n}][0]$$

### Global Constraints

These constraints must hold for **every valid solution**, regardless of the
algorithm used.

**C1 – Precedence (pickup before drop-off)**
For every passenger i ∈ {1, …, n}:

$$\text{pos}(i) < \text{pos}(i + n) \quad \text{in route } \pi$$

Passenger i can only be dropped off after they have been picked up.

**C2 – Capacity (bus load never exceeds k)**
Define the bus load after visiting the first t stops as:

$$\text{load}(t) = |\{s \leq t : \pi_s \leq n\}| - |\{s \leq t : \pi_s > n\}|$$

Then for all t ∈ {1, …, 2n}:

$$0 \leq \text{load}(t) \leq k$$

**C3 – Coverage (all stops visited exactly once)**
π is a permutation of {1, 2, …, 2n}, so every passenger is both picked up
and dropped off exactly once.

---

## Solution 0 – Greedy (`Greedy.py`)

### Algorithm-Specific Constraints

- **Selection rule**: at every step choose the **nearest unvisited reachable
  node** from the current position (nearest-neighbour greedy criterion).
- **Feasibility by construction**: constraints C1 and C2 are enforced
  during node selection, so the output route is always valid — no
  post-hoc check is needed.
- **Determinism**: given identical input, the algorithm always produces the
  same route (no randomness, no time limit).
- **Single pass**: the route is built in exactly N = 2n steps with no
  backtracking or improvement phase.

### Code Flow

| Section | What It Does |
|---------|-------------|
| **Input parsing** | Reads n, k, and the (2n+1)×(2n+1) distance matrix from stdin. |
| **Initialisation** | Sets `current_node = 0` (depot), `load = 0`, and a `visited` boolean array of size 2n+1. |
| **Construction loop** | Runs N times. Each iteration scans all unvisited nodes v and picks the closest one that satisfies both constraints: pickup v is skipped if `load ≥ k`; drop-off v+n is skipped if passenger v-n has not yet been picked up. The chosen node is appended to the route, marked visited, and `load` updated. |
| **Output** | Prints n and the completed route as space-separated integers. |

### Cost Evaluation

**Time complexity**: O(N²) — N outer steps × up to N candidate nodes
scanned per step.

**Space complexity**: O(N) for the route and visited arrays; O(N²) for
the distance matrix.

**Quality**: The greedy heuristic produces a **feasible** solution very
quickly, but offers **no optimality guarantee**. It is susceptible to
myopic choices — a locally cheap edge can force expensive detours later.
On structured instances (clustered or Euclidean distances) it tends to
produce reasonable starting points; on adversarial inputs it may be far
from optimal. Its primary value is as a fast, deterministic seed for the
local search algorithms below.

### Pseudocode

```
function solve_greedy(c, n, k):
    route        ← []
    visited      ← [False] * (N+1)
    load         ← 0
    current_node ← 0

    for step ← 1 to N:
        best_next    ← -1
        min_distance ← +∞

        for v ← 1 to N:
            if visited[v]:               continue   // already visited
            if v ≤ n and load ≥ k:       continue   // C2: would exceed capacity
            if v > n and not visited[v-n]: continue  // C1: drop-off before pickup

            if c[current_node][v] < min_distance:
                min_distance ← c[current_node][v]
                best_next    ← v

        visited[best_next] ← True
        route.append(best_next)
        current_node ← best_next

        if best_next ≤ n: load += 1    // picked up a passenger
        else:             load -= 1    // dropped off a passenger

    return route
```

> **Note for local search solutions:** Solutions 1–3 all use this exact
> greedy procedure to build their initial feasible route before applying
> their respective improvement strategies.

---

## Solution 1 – 2-opt Local Search (`LS_2-opt.py`)

### Algorithm-Specific Constraints

- **Neighborhood**: pairwise position swaps only — route[i] ↔ route[j].
- **Acceptance rule**: a swap is accepted only if it strictly **decreases**
  the total cost *and* the resulting route is **feasible** (satisfies C1 and C2).
- **Search mode**: first-improvement — the outer loop restarts as soon as one
  improving swap is found.
- **Time limit**: the improvement loop runs for at most 290 seconds.

### Code Flow

| Section | What It Does |
|---------|-------------|
| **Input parsing** | Reads n, k, and the (2n+1)×(2n+1) distance matrix from stdin. |
| **Greedy init** | Builds a feasible starting route using the Greedy heuristic (Solution 0). |
| **`calculate_swap`** | Computes the cost delta Δ for swapping positions i and j without modifying the route. Handles the adjacent (j = i+1) and non-adjacent cases separately to avoid double-counting shared edges. |
| **`is_valid`** | Verifies C1 (precedence) and C2 (capacity) by walking the route. |
| **2-opt loop** | Iterates over all pairs (i, j); swaps the two positions, runs `is_valid`, accepts if Δ < 0 and feasible, otherwise reverts. Breaks to restart scan on first acceptance. |
| **Output** | Prints n and the final route as space-separated integers. |

### Cost Evaluation

**Time complexity per iteration**: O(N²) pairs × O(1) delta calculation + O(N) validity check per accepted move.

**Space complexity**: O(N) for the route array; O(N²) for the distance matrix.

**Quality**: Converges to a **local optimum** with respect to pairwise swaps. First-improvement restarts prevent it from wasting time in a single neighbourhood scan, but the search may terminate early in a poor local optimum because no validity-preserving swap exists that reduces cost.

**Practical limitation**: For large n (close to 1000), the O(N²) inner loop (~4 × 10⁶ iterations) combined with the O(N) validity check makes each outer iteration slow; the algorithm may only complete a small number of improvement rounds within 290 seconds.

### Pseudocode

```
function solve_2opt(c, n, k):
    route ← Greedy(c, n, k)

    improved ← True
    while improved and elapsed_time < 290s:
        improved ← False

        for i ← 0 to N-1:
            for j ← i+1 to N-1:

                Δ ← calculate_swap(route, i, j, c)

                if Δ < 0:
                    swap route[i] and route[j]

                    if is_valid(route, n, k):
                        improved ← True
                        break inner loop      // first-improvement restart
                    else:
                        swap route[i] and route[j]   // revert

            if improved:
                break outer loop

    return route


function calculate_swap(route, i, j, c):
    // Compute cost change of swapping route[i] and route[j]
    pre_i  ← route[i-1]  (or depot 0 if i = 0)
    next_i ← route[i+1]  (or depot 0 if i = N-1)
    pre_j  ← route[j-1]  (or depot 0 if j = 0)
    next_j ← route[j+1]  (or depot 0 if j = N-1)

    if j = i+1:   // adjacent nodes share one edge
        Δ ← c[pre_i][route[j]] + c[route[j]][route[i]] + c[route[i]][next_j]
          - c[pre_i][route[i]] - c[route[i]][route[j]] - c[route[j]][next_j]
    else:
        Δ ← c[pre_i][route[j]] + c[route[j]][next_i]
          + c[pre_j][route[i]] + c[route[i]][next_j]
          - c[pre_i][route[i]] - c[route[i]][next_i]
          - c[pre_j][route[j]] - c[route[j]][next_j]

    return Δ
```

---

## Solution 2 – Random Walk (`LS_RandomWalk.py`)

### Algorithm-Specific Constraints

- **Neighborhood**: remove a passenger's pickup node from its current position
  and re-insert it at a random position; then do the same for its drop-off
  node at a random position **after** the pickup.
- **Acceptance rule**: always apply the move (random walk — no hill-climbing
  filter). The best solution found so far is recorded separately.
- **Feasibility gate**: only update the global best if the new route passes
  `is_valid`.
- **Cost tracking**: uses **incremental** (O(1)) cost updates rather than
  recomputing the full route cost each iteration.

### Code Flow

| Section | What It Does |
|---------|-------------|
| **Input parsing** | Reads n, k, and the distance matrix from stdin. |
| **Greedy init** | Builds the initial feasible route using the Greedy heuristic (Solution 0); computes its total cost incrementally. |
| **`remove_and_insert_and_calculate_cost`** | Removes node x from its current position, updates the cost by subtracting the two edges incident to x and adding the bridging edge, then inserts x at position i, updating cost again. Returns the new cost and the modified route. O(N) due to list index/insert. |
| **Random walk loop** | Each iteration: pick a random pickup x and a random insertion index i; re-insert x at i. Then pick a random index j ≥ i and re-insert x+n at j (ensuring drop-off stays after pickup). If the new cost is the best seen *and* the route is valid, save it; otherwise revert to the recorded best. |
| **Output** | Prints n and the best route found. |

### Cost Evaluation

**Time complexity per iteration**: O(N) for `list.index` and `list.insert`
operations (Python lists require shifting elements).

**Space complexity**: O(N) route + O(N²) matrix.

**Quality**: The random walk can escape local optima because it accepts
non-improving moves freely. However, because moves are completely random
and most will not improve the solution, progress depends heavily on luck.
For large N the O(N) per-iteration cost permits many iterations within
290 seconds, giving a reasonable exploration budget.

**Key design choice**: Always reverting to the best-known solution after a
non-improving move means the walk is effectively a **random restart around
the best solution** rather than a true unguided walk, which provides some
implicit bias toward better regions of the search space.

### Pseudocode

```
function solve_random_walk(c, n, k):
    route     ← Greedy(c, n, k)
    best_cost ← total_cost(route)
    best_route ← route[:]

    while elapsed_time < 290s:
        x ← random integer in [1, n]           // choose a passenger (pickup id)
        i ← random integer in [0, N-1]         // target insertion index for pickup

        cost, route ← remove_and_insert(route, x,   i, best_cost)
        j ← random integer in [i, N-1]         // target insertion index for drop-off
        cost, route ← remove_and_insert(route, x+n, j, cost)

        if cost < best_cost and is_valid(route, n, k):
            best_cost  ← cost
            best_route ← route[:]
        else:
            route ← best_route[:]              // revert to best

    return best_route


function remove_and_insert(route, x, i, prev_cost):
    // Remove x from its current position
    idx ← route.index(x)
    pre  ← route[idx-1]  (or 0)
    nxt  ← route[idx+1]  (or 0)
    cost ← prev_cost - c[pre][x] - c[x][nxt] + c[pre][nxt]
    new_route ← route without route[idx]

    // Insert x at position i
    pre_i ← new_route[i-1]  (or 0)
    nxt_i ← new_route[i]    (or 0)
    cost  ← cost - c[pre_i][nxt_i] + c[pre_i][x] + c[x][nxt_i]
    new_route.insert(i, x)

    return cost, new_route
```

---

## Solution 3 – Tabu Search (`TabuSearch.py`)

### Algorithm-Specific Constraints

- **Neighborhood**: pairwise position swaps (same as 2-opt).
- **Acceptance rule**: at each iteration, choose the **best feasible,
  non-tabu swap** over all N(N-1)/2 pairs. A tabu move may still be
  accepted if it satisfies the **aspiration criterion**
  (current\_cost + Δ < best\_cost).
- **Tabu memory**: a dictionary mapping each swap pair (a, b) to the
  iteration at which the prohibition expires. **Dynamic tenure**:
  each accepted move is forbidden for a random duration in
  [T\_min, T\_max] (± small jitter).
- **Escape mechanism**: if no improvement to the global best is made for
  200 consecutive iterations, restart from the best-known solution plus
  a random valid perturbation.

### Code Flow

| Section | What It Does |
|---------|-------------|
| **Input parsing** | Reads n, k, and the distance matrix from stdin. |
| **Parameter setup** | Computes T\_min = max(5, ⌊0.5√n⌋) and T\_max = max(15, ⌊1.5√n⌋) — tenure scales with problem size. |
| **Greedy init** | Builds the initial feasible route using the Greedy heuristic (Solution 0); computes its full cost. |
| **Main loop — best neighbour scan** | Iterates all (i, j) pairs; skips non-feasible swaps, tabu moves (unless aspirated), and any swap worse than the current best candidate delta. Tracks the best valid swap found. |
| **Move execution** | Applies the best swap; adds the move to `tabu_list` with a dynamic expiry; prunes expired entries. |
| **Best update / no-improve counter** | Updates the global best if cost improved; increments `no_improve` otherwise. |
| **Escape / perturbation** | When `no_improve` exceeds 200: reset to the best-known route, apply up to 200 random swaps until a feasible, non-tabu one is found, recompute cost, reset `no_improve` and iteration counter. |
| **Output** | Prints n and the **best** (not current) route. |

### Cost Evaluation

**Time complexity per iteration**: O(N²) pairs × O(N) validity check in the
worst case, though the early-termination `delta ≥ best_delta` guard prunes
many pairs cheaply.

**Space complexity**: O(N) route + O(N²) matrix + O(tabu size) dictionary
(bounded in practice by the tenure window).

**Quality**: Tabu search is significantly stronger than 2-opt or random walk
because it: (1) explores non-improving moves intentionally to escape local
optima; (2) uses memory (the tabu list) to avoid cycling; (3) dynamically
adjusts the forbidden horizon to balance diversification and intensification;
(4) retains the **global best** separately from the current working solution,
so a long diversification excursion cannot permanently damage the recorded
optimum.

**Trade-off**: The O(N²) neighbour scan is the bottleneck. For n = 1000
(N = 2000), each iteration examines ~2 × 10⁶ pairs; few full iterations
will complete within 290 seconds at large scale.

### Pseudocode

```
function solve_tabu(c, n, k):
    route         ← Greedy(c, n, k)
    current       ← route[:]
    current_cost  ← total_cost(current, c)
    best          ← current[:]
    best_cost     ← current_cost

    T_min ← max(5,  floor(0.5 * sqrt(n)))
    T_max ← max(15, floor(1.5 * sqrt(n)))
    tabu_list ← {}          // move → expiry iteration
    it ← 0;  no_improve ← 0

    while elapsed_time < 290s:

        // --- Neighbour scan ---
        best_delta ← +∞;  best_pair ← None;  best_move ← None

        for i ← 0 to N-1:
            for j ← i+1 to N-1:
                Δ ← calculate_swap(current, i, j, c)
                if Δ ≥ best_delta: continue          // prune

                a, b  ← current[i], current[j]
                move  ← (min(a,b), max(a,b))
                is_tabu ← (move ∈ tabu_list) and (tabu_list[move] > it)

                // Aspiration: allow tabu move only if it beats global best
                if is_tabu and (current_cost + Δ) ≥ best_cost: continue

                // Feasibility check
                swap current[i] and current[j]
                feasible ← is_valid(current, n, k)
                swap current[i] and current[j]       // revert tentative swap
                if not feasible: continue

                best_delta ← Δ
                best_pair  ← (i, j)
                best_move  ← move

        if best_pair is None: break                  // no valid move found

        // --- Apply best move ---
        i, j ← best_pair
        swap current[i] and current[j]
        current_cost += best_delta

        tenure ← random_int(T_min, T_max) + random_int(0, T_max // 10)
        tabu_list[best_move] ← it + tenure
        tabu_list ← { m: exp for (m, exp) in tabu_list if exp > it }  // prune

        // --- Update global best ---
        if current_cost < best_cost:
            best       ← current[:]
            best_cost  ← current_cost
            no_improve ← 0
        else:
            no_improve += 1

        it += 1

        // --- Escape local optimum ---
        if no_improve > 200:
            current    ← best[:]
            it_escape  ← 0
            escaped    ← False

            while not escaped and it_escape < 200:
                i ← random_int(0, N-1)
                j ← random_int(i, N-1)
                swap current[i] and current[j]
                move ← (min(current[i], current[j]),
                         max(current[i], current[j]))
                if is_valid(current, n, k) and move not in tabu_list:
                    escaped ← True
                else:
                    swap current[i] and current[j]   // revert
                it_escape += 1

            current_cost ← total_cost(current, c)
            no_improve   ← 0
            it           ← 0

    return best
```

---

## Summary Comparison

| Feature | Greedy | 2-opt | Random Walk | Tabu Search |
|---------|--------|-------|-------------|-------------|
| Initialization | — (standalone) | Greedy (Sol. 0) | Greedy (Sol. 0) | Greedy (Sol. 0) |
| Neighbourhood | None | Pairwise swap | Remove & re-insert | Pairwise swap |
| Acceptance | N/A (construction) | First improving | Always (random walk) | Best non-tabu |
| Escape mechanism | None | None | Implicit (random) | Explicit (perturbation + restart) |
| Memory | None | None | None | Tabu list (dictionary) |
| Aspiration criterion | No | No | No | Yes (beats global best) |
| Optimum type | Greedy feasible solution | Strict local optimum | Stochastic best | Near-global (memory-guided) |
| Time complexity | O(N²) one-shot | O(N²) + O(N) per iter | O(N) per iter | O(N²) + O(N) per iter |
| Time limit needed | No | Yes (290 s) | Yes (290 s) | Yes (290 s) |
| Best suited for | Seed / baseline | Small–medium n | Large n (fast iterations) | Medium–large n (quality) |
