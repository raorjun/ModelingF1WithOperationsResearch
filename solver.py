from ortools.linear_solver import pywraplp

# Define the solver
solver = pywraplp.Solver.CreateSolver('SCIP')

# Number of laps in the race
n_laps = 71

# Fixed pit stop time loss
S = 20.41

# Decision variables
P = solver.IntVar(1, n_laps, 'P')
t_p = [solver.IntVar(0, n_laps, f't_p[{i}]') for i in range(n_laps)]
c_i = [solver.IntVar(0, 2, f'c_i[{i}]') for i in range(n_laps)]  # 0 for soft, 1 for medium, 2 for hard

# Indicator variables
delta_soft = solver.BoolVar('delta_soft')
delta_medium = solver.BoolVar('delta_medium')
delta_hard = solver.BoolVar('delta_hard')

# Logical constraints for indicator variables
solver.Add(delta_soft <= solver.Sum([c_i[i] == 0 for i in range(n_laps)]))
solver.Add(delta_medium <= solver.Sum([c_i[i] == 1 for i in range(n_laps)]))
solver.Add(delta_hard <= solver.Sum([c_i[i] == 2 for i in range(n_laps)]))

# Ensure at least two unique compounds are used
solver.Add(delta_soft + delta_medium + delta_hard >= 2)

# Lap time equations as piecewise linear functions
def lap_time(i, tire_type):
    if tire_type == 0:  # soft
        return 0.1 * i + 68
    elif tire_type == 1:  # medium
        return 0.05 * i + 69.6
    elif tire_type == 2:  # hard
        return 0.04 * i + 69.8

# Objective function
objective = solver.Sum([lap_time(i, c_i[i].solution_value()) for i in range(n_laps)]) + P * S
solver.Minimize(objective)

# Constraints
# Maximum stint length constraints
for i in range(n_laps):
    solver.Add(solver.Sum([c_i[j] == 0 for j in range(i, min(i+15, n_laps))]) <= 15)
    solver.Add(solver.Sum([c_i[j] == 1 for j in range(i, min(i+25, n_laps))]) <= 25)
    solver.Add(solver.Sum([c_i[j] == 2 for j in range(i, min(i+30, n_laps))]) <= 30)

# Solve the model
status = solver.Solve()

# Output the results
if status == pywraplp.Solver.OPTIMAL:
    print(f'Optimal number of pit stops: {P.solution_value()}')
    print('Pit stop timings:', [t_p[p].solution_value() for p in range(n_laps) if t_p[p].solution_value() != 0])
    print('Tire compounds used:', ['soft' if c_i[i].solution_value() == 0 else 'medium' if c_i[i].solution_value() == 1 else 'hard' for i in range(n_laps)])
else:
    print('No optimal solution found.')
