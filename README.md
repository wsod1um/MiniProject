# CBUS - Heuristic and Metaheuristic approach

## Overview
This contains the solution for CBUS problem.

**Heuristic :** 

Solution 0 – Greedy (`Greedy.py`)Solution 0 – Greedy (`Greedy.py`)\
Solution 1 – Swap Move Local Search (`LS_Swap.py`)\
Solution 2 – Random Walk (`LS_RandomWalk.py`)\

**Metaheuristic : **

Solution 3 – Tabu Search (`TabuSearch.py`)\ 

---

## Installation

Run python code directly
Input format is the same as on HUSTACK

---

## Solution Comparison

| Feature | Greedy | Swap-Move LS | Random Walk | Tabu Search |
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
