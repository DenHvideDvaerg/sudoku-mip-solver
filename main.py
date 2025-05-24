from sudoku import Sudoku
from sudoku_mip_solver import SudokuMIPSolver
import time

width = 3
height = 3
puzzle = Sudoku(width, height).difficulty(0.5)

puzzle.show()

solution = puzzle.solve()
solution.show()

board = puzzle.board

# sudoku_string = "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
# board = []
# for i in range(0, 81, 9):
#     row = []
#     for j in range(9):
#         value = int(sudoku_string[i + j])
#         row.append(value if value != 0 else None)
#     board.append(row)

print("Sudoku Bogit rm -r --cached __pycache__/ard:")
for row in board:
    print(row)

# Solve onces
# Initial solve
solver = SudokuMIPSolver(board, width, height)
start_time = time.time()
has_solution = solver.solve()
found_solution = solver.current_solution
if has_solution:
    print("Solution found:")
    for row in solver.current_solution:
        print(row)


# # Find all solutions
# solver = SudokuMIPSolver(board, width, height)
# all_solutions = solver.find_all_solutions(max_solutions=10)
# print(f"\nFound {len(all_solutions)} solution(s):")

# for idx, solution in enumerate(all_solutions):
#     print(f"\nSolution {idx + 1}:")
#     for row in solution:
#         print(row)

# solutions = []

# if has_solution:
#     solutions.append(solver.current_solution)
#     print(f"Found solution {len(solutions)} in {time.time() - start_time:.4f} seconds:")
#     for row in solver.current_solution:
#         print(row)
    
#     # Continue finding all solutions
#     while True:
#         # Add constraint to exclude current solution
#         solver.cut_current_solution()
        
#         # Try to find another solution
#         success = solver.solve()
        
#         if success and solver.current_solution:
#             solutions.append(solver.current_solution)
#             print(f"\nFound solution {len(solutions)} in {time.time() - start_time:.4f} seconds:")
#             for row in solver.current_solution:
#                 print(row)
#         else:
#             # No more solutions
#             print("No more solutions found.")
#             break
    
#     total_time = time.time() - start_time
#     print(f"\nFound {len(solutions)} solution(s) in total, in {total_time:.4f} seconds.")
#     if len(solutions) == 1:
#         print("The solution is unique!")
#     else:
#         print("Multiple solutions exist for this puzzle.")
# else:
#     print("No solution found!")

# solver.print_model()