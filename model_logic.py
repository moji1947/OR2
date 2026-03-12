import pulp as pl

def solve_logistics(customers_data, truck_cap, budget_limit, dist_limit, drop_limit, cost_rate):
    """
    ฟังก์ชันสำหรับคำนวณหาแผนการจัดส่งที่เหมาะสมที่สุด
    """
    W = customers_data['Weight'].tolist()
    Dist = customers_data['Distance'].tolist()
    Names = customers_data['Customer'].tolist()
    Cost = [d * cost_rate for d in Dist]
    
    Truck_Cap = [truck_cap, truck_cap] # รถ 2 คัน
    Trucks, Customers = range(len(Truck_Cap)), range(len(W))
    
    m = pl.LpProblem("Fleet_Optimization", pl.LpMaximize)
    X = pl.LpVariable.dicts("X", [(i,j) for i in Trucks for j in Customers], 0, 1, pl.LpBinary)

    # Objective
    m += pl.lpSum(W[j] * X[(i,j)] for i in Trucks for j in Customers)

    # Constraints
    for i in Trucks:
        m += pl.lpSum([W[j] * X[(i,j)] for j in Customers]) <= Truck_Cap[i]
        m += pl.lpSum([X[(i,j)] for j in Customers]) <= drop_limit
        m += pl.lpSum([Dist[j] * X[(i,j)] for j in Customers]) <= dist_limit
        m += pl.lpSum([Cost[j] * X[(i,j)] for j in Customers]) <= budget_limit

    for j in Customers:
        m += pl.lpSum([X[(i,j)] for i in Trucks]) <= 1

    m.solve(pl.PULP_CBC_CMD(msg=0))
    
    return m, X, Trucks, Customers, Names, W, Dist