from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

def north_west_corner(supply, demand, costs):
    print("North West Corner  Method start")
    rows, cols = len(supply), len(demand)
    allocation = [[0] * cols for _ in range(rows)]
    i, j = 0, 0
    total_cost = 0
    highlighted_cells = []

    while i < rows and j < cols:
        allocation_value = min(supply[i], demand[j])
        allocation[i][j] = allocation_value
        total_cost += allocation_value * costs[i][j]
        supply[i] -= allocation_value
        demand[j] -= allocation_value
        highlighted_cells.append((i, j))

        if supply[i] == 0:
            i += 1
        elif demand[j] == 0:
            j += 1

    return {"allocation": allocation, "totalCost": total_cost, "highlightedCells": highlighted_cells}

def least_cost_method(supply, demand, costs):
    print("Least cost  Method start")
    rows, cols = len(supply), len(demand)
    allocation = [[0] * cols for _ in range(rows)]
    total_cost = 0
    highlighted_cells = []

    while any(supply) and any(demand):
        min_cost = float('inf')
        min_cell = (-1, -1)
        
        
        for i in range(rows):
            for j in range(cols):
                if supply[i] > 0 and demand[j] > 0 and costs[i][j] < min_cost:
                    min_cost = costs[i][j]
                    min_cell = (i, j)
        
        i, j = min_cell
        allocation_value = min(supply[i], demand[j])
        allocation[i][j] = allocation_value
        total_cost += allocation_value * costs[i][j]
        supply[i] -= allocation_value
        demand[j] -= allocation_value
        highlighted_cells.append((i, j))

    return {"allocation": allocation, "totalCost": total_cost, "highlightedCells": highlighted_cells}

def vogel_approximation(supply, demand, costs):
    print("Vogel's Approximation Method start")
    rows, cols = len(supply), len(demand)
    allocation = [[0] * cols for _ in range(rows)]
    total_cost = 0
    highlighted_cells = []

    
    row_penalties = []
    col_penalties = []

    def calculate_penalties():
        nonlocal row_penalties, col_penalties
        
        row_penalties = []
        for i in range(rows):
            if supply[i] > 0:
                sorted_row = sorted([(costs[i][j], j) for j in range(cols) if demand[j] > 0], key=lambda x: x[0])
                if len(sorted_row) > 1:
                    row_penalties.append((sorted_row[1][0] - sorted_row[0][0], i))
                else:
                    row_penalties.append((0, i))

        
        col_penalties = []
        for j in range(cols):
            if demand[j] > 0:
                sorted_col = sorted([(costs[i][j], i) for i in range(rows) if supply[i] > 0], key=lambda x: x[0])
                if len(sorted_col) > 1:
                    col_penalties.append((sorted_col[1][0] - sorted_col[0][0], j))
                else:
                    col_penalties.append((0, j))

    calculate_penalties()

    
    while any(supply) and any(demand):
        
        max_row_penalty = max(row_penalties, key=lambda x: x[0], default=(None, -1))
        max_col_penalty = max(col_penalties, key=lambda x: x[0], default=(None, -1))

        if max_row_penalty[0] >= max_col_penalty[0]:
            _, i = max_row_penalty
            sorted_row = sorted([(costs[i][j], j) for j in range(cols) if demand[j] > 0], key=lambda x: x[0])
            if not sorted_row:
                break
            j = sorted_row[0][1]
        else:
            _, j = max_col_penalty
            sorted_col = sorted([(costs[i][j], i) for i in range(rows) if supply[i] > 0], key=lambda x: x[0])
            if not sorted_col:
                break
            i = sorted_col[0][1]

        allocation_value = min(supply[i], demand[j])
        allocation[i][j] = allocation_value
        total_cost += allocation_value * costs[i][j]
        supply[i] -= allocation_value
        demand[j] -= allocation_value
        highlighted_cells.append((i, j))

        
        calculate_penalties()

    return {"allocation": allocation, "totalCost": total_cost, "highlightedCells": highlighted_cells}

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    method = data.get("method")
    supply = data.get("supply")
    demand = data.get("demand")
    costs = data.get("costs")

    if not supply or not demand or not costs:
        return jsonify({"error": "Invalid input"}), 400

    if sum(supply) != sum(demand):
        return jsonify({"error": "Supply and demand totals do not match"}), 400

    if method == "north-west":
        result = north_west_corner(supply, demand, costs)
    elif method == "least-cost":
        result = least_cost_method(supply, demand, costs)
    elif method == "vogel":
        result = vogel_approximation(supply, demand, costs)
    else:
        return jsonify({"error": "Invalid method"}), 400

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
