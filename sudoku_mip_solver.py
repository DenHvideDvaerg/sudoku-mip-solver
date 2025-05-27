from pulp import *

class SudokuMIPSolver: 
    def __init__(self, board: list[list[int]], sub_grid_width: int, sub_grid_height: int = None):
        # Validate board dimensions and values
        if sub_grid_width < 1:
            raise ValueError("Sub-grid width must be at least 1")
        
        self.sub_grid_width = sub_grid_width
        self.sub_grid_height = sub_grid_height if sub_grid_height is not None else sub_grid_width
        
        if self.sub_grid_height < 1:
            raise ValueError("Sub-grid height must be at least 1")
            
        self.size = self.sub_grid_width * self.sub_grid_height
        
        # Check board dimensions
        if not board or len(board) != self.size:
            raise ValueError(f"Board must have exactly {self.size} rows")
        
        for r, row in enumerate(board):
            if len(row) != self.size:
                raise ValueError(f"Row {r} has {len(row)} elements, should have {self.size}")
        
        # Validate cell values
        for r, row in enumerate(board):
            for c, val in enumerate(row):
                if val is not None and (not isinstance(val, int) or val < 1 or val > self.size):
                    raise ValueError(f"Invalid value {val} at position ({r},{c}). Must be None or integer from 1 to {self.size}")
        
        self.board = board
        self.model = None
        self.current_solution = None
        self.cut_constraints = []

    def build_model(self):
        """Build the MIP model with all Sudoku constraints."""
        # Create the model
        self.model = LpProblem("SudokuSolver",LpMinimize)
        
        # Create variables - x[row,column,value] = 1 if cell (row,column) has value
        self.variables = LpVariable.dicts("x", 
                                              ((row, column, value) for row in range(self.size) 
                                                                    for column in range(self.size) 
                                                                    for value in range(1, self.size+1)),
                                              cat="Binary"
        )
        
        # One value per cell
        for r in range(self.size):
            for c in range(self.size):
                constraint_name = f"cell_{r+1}_{c+1}_one_value"
                self.model += lpSum(self.variables[r, c, v] for v in range(1, self.size+1)) == 1, constraint_name

        # One of each value per row
        for r in range(self.size):
            for v in range(1, self.size+1):
                constraint_name = f"row_{r+1}_has_value_{v}"
                self.model += lpSum(self.variables[r, c, v] for c in range(self.size)) == 1, constraint_name
        
        # One of each value per column
        for c in range(self.size):
            for v in range(1, self.size+1):
                constraint_name = f"col_{c+1}_has_value_{v}"
                self.model += lpSum(self.variables[r, c, v] for r in range(self.size)) == 1, constraint_name
        
        # One of each value per box (sub-grid)
        for box_r in range(self.size // self.sub_grid_height):
            for box_c in range(self.size // self.sub_grid_width):
                for v in range(1, self.size+1):
                    constraint_name = f"box_{box_r+1}_{box_c+1}_has_value_{v}"
                    self.model += lpSum(self.variables[box_r*self.sub_grid_height + r, box_c*self.sub_grid_width + c, v] 
                                    for r in range(self.sub_grid_height) 
                                    for c in range(self.sub_grid_width)) == 1, constraint_name
            
        # Dummy objective as this is a feasibility problem
        self.model += 0
        
        # Fix initial values from the board
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] is not None:
                    constraint_name = f"fixed_value_at_{r+1}_{c+1}"
                    self.model += self.variables[r, c, self.board[r][c]] == 1, constraint_name
        
        return self.model
    

    def solve(self):
        """Solve the Sudoku puzzle and return bool indicating if a solution was found."""
        if not self.model:
            self.build_model()
            
        # Solve the model
        self.model.solve(pulp.PULP_CBC_CMD(msg=False))
        
        # Extract solution
        if self.model.status == LpStatusOptimal:
            self.current_solution = self.extract_solution()
            return True
        else:
            # Clear the current solution to indicate no feasible solution was found
            self.current_solution = None
            return False

    def find_all_solutions(self, max_solutions=None):
        """Find all solutions to the Sudoku puzzle, up to max_solutions."""
        all_solutions = []
        
        # Build and solve the model
        if not self.model:
            self.build_model()
        
        # Find solutions until the problem becomes infeasible
        while max_solutions is None or len(all_solutions) < max_solutions:
            if self.solve():
                  # Deep copy of the current solution
                solution = [row[:] for row in self.current_solution]
                all_solutions.append(solution)
                self.cut_current_solution()
            else:
                break
        
        return all_solutions

    def extract_solution(self):
        """Extract the solution from the model variables."""
        solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                for v in range(1, self.size+1):
                    if value(self.variables[r, c, v]) == 1:
                        solution[r][c] = v
        return solution

    def cut_current_solution(self):
        """Add a constraint to exclude the current solution from future searches."""
        if self.current_solution is None:
            raise ValueError("No current solution to cut.")
        
        # Create the constraint
        constraint_name = f"cut_{len(self.cut_constraints) + 1}"
        cut_constraint = lpSum(self.variables[r, c, self.current_solution[r][c]] 
                        for r in range(self.size) 
                        for c in range(self.size)) <= self.size * self.size - 1
        
        # Add it to the model
        self.model += cut_constraint, constraint_name
        
        # Store reference to this constraint
        self.cut_constraints.append((constraint_name, cut_constraint))

    def get_solution(self):
        """Get the current solution."""
        if self.current_solution is None:
            raise ValueError("No solution found yet. Please call solve() first.")
        return self.current_solution
    
    def print_model(self):
        """Print the model in a readable format."""
        print(f"Objective: {self.model.objective.value()}")
        print(f"Status: {LpStatus[self.model.status]}")
        print("Model:")
        for constraint in self.model.constraints.values():
            print(f"{constraint.name}: {constraint}")
        for v in self.model.variables():
            print(f"{v.name} = {v.varValue}")
        
    def reset_model(self):
        """
        Remove all solution cuts from the model, restoring it to the original constraints.
        """
        if not self.cut_constraints:
            return  # No cuts to remove
            
        if self.model is None:
            return  # No model exists yet
        
        # Remove each constraint by name
        for name, _ in self.cut_constraints:
            if name in self.model.constraints:
                del self.model.constraints[name]
                
        # Clear the list of cut constraints
        self.cut_constraints = []
        self.current_solution = None
        
        return self.model
    
    @classmethod
    def from_string(cls, sudoku_string, sub_grid_width = 3, sub_grid_height=None):
        """
        Create a SudokuMIPSolver instance from a string representation.
        
        Parameters:
        - sudoku_string: A string where each character represents a cell value.
                         Use '0', '.', or any non-digit character for empty cells.
        - sub_grid_width: Width of the sub-grid (defaults to 3 for standard Sudoku)
        - sub_grid_height: Height of the sub-grid (defaults to sub_grid_width)
        
        Returns:
        - A new SudokuMIPSolver instance
        
        Example:
            "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
            represents a 9x9 Sudoku with certain cells filled.
        """
        if sub_grid_height is None:
            sub_grid_height = sub_grid_width
            
        size = sub_grid_width * sub_grid_height
        
        # Remove any whitespace or newlines
        sudoku_string = ''.join(sudoku_string.split())
        
        # Check if the string has the correct length
        if len(sudoku_string) != size * size:
            raise ValueError(f"String length must be {size * size} for a {size}x{size} Sudoku")
        
        # Parse the string into a board
        board = []
        for i in range(0, len(sudoku_string), size):
            row = []
            for j in range(size):
                char = sudoku_string[i + j]
                # Convert to integer if it's a digit and not 0
                if char.isdigit() and char != '0':
                    row.append(int(char))
                else:
                    row.append(None)  # Empty cell
            board.append(row)
        
        return cls(board, sub_grid_width, sub_grid_height)
    
    def pretty_print(self, board=None):
        """
        Pretty print the Sudoku board with grid lines showing sub-grids.
        
        Parameters:
        - board: The board to print. If None, prints the current solution.
        
        Returns:
        - None (prints to console)
        """
        if board is None:
            if self.current_solution is None:
                raise ValueError("No solution available to print")
            board = self.current_solution
        
        # Determine characters needed for each cell based on puzzle size
        cell_width = len(str(self.size)) + 1  # +1 for spacing
        
        # Horizontal separator for sub-grids
        h_separator = "+" + "+".join(["-" * (cell_width * self.sub_grid_width) for _ in range(self.sub_grid_height)]) + "+"
        
        for r in range(self.size):
            # Print horizontal separator at the beginning of each sub-grid row
            if r % self.sub_grid_height == 0:
                print(h_separator)
            
            row_str = ""
            for c in range(self.size):
                # Print vertical separator at the beginning of each sub-grid column
                if c % self.sub_grid_width == 0:
                    row_str += "|"
                
                # Get the value, ensure it's right-aligned within its cell width
                value = board[r][c] if board[r][c] is not None else "."
                row_str += f"{value}".rjust(cell_width)
            
            # End the row with a vertical separator
            row_str += "|"
            print(row_str)
        
        # Print horizontal separator at the end
        print(h_separator)