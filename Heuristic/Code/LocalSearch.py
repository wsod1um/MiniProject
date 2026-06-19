import sys
import time

def solve():
    
    start_time = time.perf_counter()
    input_data = sys.stdin.read().split()
    
    n = int(input_data[0])
    k = int(input_data[1])

    c = []

    index = 2
    for _ in range(2*n+1):
        row = []
        for _ in range(2*n+1):
            row.append(int(input_data[index]))
            index +=1
        c.append(row)

    # Initial Valid Route: Pickup and drop off each passenger right away 
    route = []
    for i in range(1,n+1):
        route.append(i)
        route.append(i+n)

    #Check validity of route
    def is_valid(route,n,k):
        load = 0
        visited = [False]*(2*n+1)
        for i in route:
            if i <= n:
                load += 1
                visited[i] = True
                if load > k:
                    return False
            else:
                if visited[i-n] == False:
                    return False
                load -= 1
        return True

    # Calculate the expected delta when swapping two vertices by adding and subtracting edges
    def calculate_swap(route,i,j,c):
        if i > j:
            i, j = j, i
        pre_i = route[i-1] if i > 0 else 0
        pre_j = route[j-1] if j > 0 else 0
        next_i = route[i+1] if i < len(route)-1 else 0
        next_j = route[j+1] if j < len(route)-1 else 0
        if j == i+1:
            delta = c[pre_i][route[j]] + c[route[j]][route[i]] + c[route[i]][next_j]
            delta -= (c[pre_i][route[i]] + c[route[i]][route[j]] + c[route[j]][next_j])
        else:
            delta = c[pre_i][route[j]]+c[route[j]][next_i]+c[pre_j][route[i]]+c[route[i]][next_j]
            delta -= c[pre_i][route[i]]+c[route[i]][next_i]+c[pre_j][route[j]]+c[route[j]][next_j]

        return delta

    
    while time.perf_counter() - start_time < 300:
        improved = False

        for i in range(2*n):
            for j in range(i+1,2*n):
                route[i],route[j] = route[j],route[i]
                if is_valid(route,n,k):
                    route[i],route[j] = route[j],route[i]
                    current_delta = calculate_swap(route,i,j,c)
                    if current_delta < 0:
                        route[i], route[j] = route[j], route[i]
                        improved = True
                        break
                else:
                    route[i],route[j] = route[j],route[i]
            if improved:
                break
        if not improved:
            break

    print(n)
    print(" ".join(map(str,route)))
if __name__ == '__main__':
    solve()
