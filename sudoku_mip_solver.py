import pulp
import random

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
        self.model = pulp.LpProblem("SudokuSolver",pulp.LpMinimize)
        
        # Create variables - x[row,column,value] = 1 if cell (row,column) has value
        self.variables = {}
        for r in range(self.size):
            for c in range(self.size):
                for v in range(1, self.size+1):
                    # Variable name uses 1-based indexing for readability, but are stored with 0-based indexing
                    var_name = f"x_({r+1},{c+1},{v})"
                    self.variables[r, c, v] = pulp.LpVariable(var_name, cat="Binary")
        
        # One value per cell
        for r in range(self.size):
            for c in range(self.size):
                constraint_name = f"cell_{r+1}_{c+1}_one_value"
                self.model += pulp.lpSum(self.variables[r, c, v] for v in range(1, self.size+1)) == 1, constraint_name

        # One of each value per row
        for r in range(self.size):
            for v in range(1, self.size+1):
                constraint_name = f"row_{r+1}_has_value_{v}"
                self.model += pulp.lpSum(self.variables[r, c, v] for c in range(self.size)) == 1, constraint_name
        
        # One of each value per column
        for c in range(self.size):
            for v in range(1, self.size+1):
                constraint_name = f"col_{c+1}_has_value_{v}"
                self.model += pulp.lpSum(self.variables[r, c, v] for r in range(self.size)) == 1, constraint_name
        
        # One of each value per box (sub-grid)
        for box_r in range(self.size // self.sub_grid_height):
            for box_c in range(self.size // self.sub_grid_width):
                for v in range(1, self.size+1):
                    constraint_name = f"box_{box_r+1}_{box_c+1}_has_value_{v}"
                    self.model += pulp.lpSum(self.variables[box_r*self.sub_grid_height + r, box_c*self.sub_grid_width + c, v] 
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
    
    def solve(self, show_output=False):
        """Solve the Sudoku puzzle and return bool indicating if a solution was found."""
        if not self.model:
            self.build_model()
            
        # Solve the model
        self.model.solve(pulp.PULP_CBC_CMD(msg=show_output))
        
        # Extract solution
        if self.model.status == pulp.LpStatusOptimal:
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
                    if pulp.value(self.variables[r, c, v]) == 1:
                        solution[r][c] = v
        return solution

    def cut_current_solution(self):
        """Add a constraint to exclude the current solution from future searches."""
        if self.current_solution is None:
            raise ValueError("No current solution to cut.")
        
        # Create the constraint
        constraint_name = f"cut_{len(self.cut_constraints) + 1}"
        cut_constraint = pulp.lpSum(self.variables[r, c, self.current_solution[r][c]] 
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
    
    def to_string(self, board=None, delimiter=None):
        """
        Convert a board to a string representation.

        Parameters:
        - board: The board to convert. If None, uses the instance's board.
        - delimiter: The delimiter to use between values. If None, values are
                     concatenated directly for boards up to 9x9. For larger boards,
                     a space is used as a default delimiter.

        Returns:
        - A string representation of the board.
        """
        target_board = board if board is not None else self.board

        if self.size > 9 and delimiter is None:
            delimiter = ' '

        flat_board = []
        for r in range(self.size):
            for c in range(self.size):
                value = target_board[r][c]
                flat_board.append(str(value if value is not None else 0))

        if delimiter is not None:
            return delimiter.join(flat_board)
        else:
            return "".join(flat_board)
    
    def print_model(self):
        """Print the model in a readable format."""
        print(f"Objective: {self.model.objective.value()}")
        print(f"Status: {pulp.LpStatus[self.model.status]}")
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

    # TODO: Pass random_seed to solver (when that is implemented)
    @classmethod
    def generate_random_puzzle(cls, sub_grid_width=3, sub_grid_height=None, target_difficulty=0.75, 
                        unique_solution=True, max_attempts=100, random_seed=None):
        """
        Generate a random Sudoku puzzle with a specified difficulty level.
        
        Parameters:
        - sub_grid_width: Width of the sub-grid (defaults to 3 for standard 9x9 Sudoku)
        - sub_grid_height: Height of the sub-grid (defaults to sub_grid_width)
        - target_difficulty: Float between 0.0 and 1.0 controlling number of clues
                            (0.0 = maximum clues/easiest, 1.0 = minimum clues/hardest)
                            This is a target and may not be achieved exactly if unique_solution=True
        - unique_solution: Whether the puzzle must have exactly one solution
        - max_attempts: Maximum number of attempts to achieve target difficulty with unique solution
        - random_seed: Optional seed for random number generator
        
        Returns:
        - A new SudokuMIPSolver instance with the generated puzzle
        - The actual difficulty achieved (may differ from target if unique_solution=True)
        """
        
        # Set random seed if provided
        if random_seed is not None:
            random.seed(random_seed)
        
        if sub_grid_height is None:
            sub_grid_height = sub_grid_width
            
        size = sub_grid_width * sub_grid_height
        
        # Validate difficulty parameter
        if not 0.0 <= target_difficulty <= 1.0:
            raise ValueError("Difficulty must be between 0.0 and 1.0")
            
        # Create and initialize the board with values on diagonal sub-grids
        initial_board = cls._initialize_puzzle_grid(size, sub_grid_width, sub_grid_height)

        # Solve the initial board to get a complete valid solution
        solver = cls(initial_board, sub_grid_width, sub_grid_height)
        if not solver.solve():
            raise RuntimeError("Failed to generate initial solution")
        
        complete_solution = [row[:] for row in solver.current_solution]
        
        # Calculate target clues based on difficulty
        total_cells = size * size
        
        # Set minimum number of clues
        # For 9x9 puzzles, mathematical studies have shown 17 is the minimum
        # For other sizes, we use the size as a reasonable lower bound
        min_clues = max(1, size)
        if size == 9:
            min_clues = 17  # Known theoretical minimum for standard 9x9 Sudoku (https://arxiv.org/abs/1201.0749)
        max_clues = total_cells  # Allow completely filled puzzles
        
        # Map difficulty from 0.0-1.0 to number of clues (inverse relationship)
        target_clues = int(min_clues + (1 - target_difficulty) * (max_clues - min_clues))
        
        # Start with the complete solution and remove cells to reach target difficulty
        current_board = [row[:] for row in complete_solution]
        current_clues = total_cells
        
        # Create ordered list of positions and shuffle for randomness
        positions = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(positions)
        
        # Track positions we've tried to remove
        tried_positions = set()
        
        # Apply cell removal strategy based on whether unique solution is required
        if unique_solution:
            max_iterations = min(max_attempts, total_cells)
            iteration = 0
            
            # Try aggressive removal first to quickly get closer to target
            aggressive_board, aggressive_clues, aggressive_success = cls._try_aggressive_removal(
                complete_solution, positions[:], target_clues, min_clues, 
                sub_grid_width, sub_grid_height
            )
            
            if aggressive_success:
                current_board = aggressive_board
                current_clues = aggressive_clues
            
            # Main removal loop - remove cells while preserving unique solution
            while current_clues > target_clues and iteration < max_iterations and tried_positions != set(positions):
                # Find positions we haven't tried yet
                untried_positions = [pos for pos in positions if pos not in tried_positions]
                if not untried_positions:
                    break
                    
                # Try batch removal when we're far from target (speeds up generation)
                if current_clues > target_clues + 10 and iteration < max_iterations // 3:
                    batch_board, batch_clues, batch_success = cls._try_batch_cell_removal(
                        current_board, untried_positions, current_clues, target_clues,
                        sub_grid_width, sub_grid_height, tried_positions
                    )
                    
                    if batch_success:
                        current_board = batch_board
                        current_clues = batch_clues
                        iteration += 1
                        continue
                
                # Single cell removal when closer to target or batch removal failed
                r, c = random.choice(untried_positions)
                tried_positions.add((r, c))
                
                # Remember the value we're removing
                temp_val = current_board[r][c]
                current_board[r][c] = None
                
                # Check if still unique solution with error handling
                try:
                    test_solver = cls(current_board, sub_grid_width, sub_grid_height)
                    solutions = test_solver.find_all_solutions(max_solutions=2)
                    
                    if len(solutions) == 1:
                        # Success - we can keep this cell removed
                        current_clues -= 1
                    else:
                        # Not unique anymore, put back the value
                        current_board[r][c] = temp_val
                except Exception:
                    # On error, put back the value
                    current_board[r][c] = temp_val
                
                iteration += 1
        else:
            # If unique solution not required, simply remove cells until target is reached
            for r, c in positions:
                if current_clues <= target_clues:
                    break
                current_board[r][c] = None
                current_clues -= 1
        
        # Calculate the actual difficulty achieved
        actual_clues = sum(1 for r in range(size) for c in range(size) if current_board[r][c] is not None)
        
        # Calculate normalized difficulty from 0.0 (easiest) to 1.0 (hardest)
        # using the theoretical minimum clues as the hardest difficulty
        actual_difficulty = 1 - ((actual_clues - min_clues) / (max_clues - min_clues))
        
        return cls(current_board, sub_grid_width, sub_grid_height), actual_difficulty
    
    @classmethod
    def _initialize_puzzle_grid(cls, size, sub_grid_width, sub_grid_height):
        """
        Initialize an empty Sudoku grid and fill the diagonal sub-grids with random values.
        This creates a valid starting point for puzzle generation.
        
        Parameters:
        - size: Size of the Sudoku grid (width/height)
        - sub_grid_width: Width of each sub-grid
        - sub_grid_height: Height of each sub-grid
        
        Returns:
        - An initialized board with diagonal sub-grids filled
        """
        
        # Create an empty board
        board = [[None for _ in range(size)] for _ in range(size)]
        
        # For non-square sub-grids, we need to be careful about the stride when filling diagonal boxes
        # to ensure we don't get out of bounds or overlap
        
        # Calculate how many sub-grids we have in each dimension
        num_vertical_blocks = size // sub_grid_height
        num_horizontal_blocks = size // sub_grid_width
        
        # We'll fill the minimum number of diagonal blocks possible
        num_diagonal_blocks = min(num_vertical_blocks, num_horizontal_blocks)
        
        # Fill diagonal sub-grids
        for block_idx in range(num_diagonal_blocks):
            # Calculate the starting indices for this diagonal block
            start_row = block_idx * sub_grid_height
            start_col = block_idx * sub_grid_width
            
            # Get valid values for this sub-grid (1 to size)
            values = list(range(1, size + 1))
            random.shuffle(values)
            
            # Fill the diagonal sub-grid
            for r in range(sub_grid_height):
                for c in range(sub_grid_width):
                    row_idx = start_row + r
                    col_idx = start_col + c
                    if row_idx < size and col_idx < size:
                        board[row_idx][col_idx] = values.pop(0)
        
        return board
    
    @classmethod
    def _try_aggressive_removal(cls, complete_solution, positions, target_clues, min_clues, 
                               sub_grid_width, sub_grid_height):
        """
        Attempt aggressive cell removal to quickly approach target difficulty.
        
        Parameters:
        - complete_solution: The complete solved Sudoku board
        - positions: List of all cell positions (shuffled)
        - target_clues: Target number of clues to keep
        - min_clues: Minimum number of clues required
        - sub_grid_width, sub_grid_height: Dimensions of sub-grids
        
        Returns:
        - tuple: (board, clues_count, success)
          - board: Modified board if successful, copy of input board if failed
          - clues_count: Number of clues in the returned board
          - success: Boolean indicating whether aggressive removal succeeded
        """

        # Copy the complete solution to work on
        board = [row[:] for row in complete_solution]
        total_cells = len(board) * len(board[0])
        current_clues = total_cells
        
        # Calculate an aggressive target (try to remove 10% more than needed)
        aggressive_clues = max(min_clues, target_clues - int(0.1 * total_cells))
        
        # Remove cells to reach aggressive target
        for r, c in positions:
            if current_clues <= aggressive_clues:
                break
            board[r][c] = None
            current_clues -= 1
        
        try:
            # Check if still has a unique solution
            test_solver = cls(board, sub_grid_width, sub_grid_height)
            solutions = test_solver.find_all_solutions(max_solutions=2)
            
            if len(solutions) == 1:
                # Success! We've found a valid aggressive starting point
                return board, current_clues, True
        except Exception:
            # If solution finding fails, return original board
            pass
            
        # If we get here, aggressive removal failed
        return [row[:] for row in complete_solution], total_cells, False
    
    @classmethod
    def _try_batch_cell_removal(cls, current_board, untried_positions, current_clues, target_clues, 
                               sub_grid_width, sub_grid_height, tried_positions):
        """
        Try removing multiple cells at once to speed up puzzle generation.
        
        Parameters:
        - current_board: Current state of the puzzle
        - untried_positions: List of positions not yet tried for removal
        - current_clues: Current number of clues in the puzzle
        - target_clues: Target number of clues
        - sub_grid_width, sub_grid_height: Dimensions of sub-grids
        - tried_positions: Set of already tried positions (will be modified)
        
        Returns:
        - tuple: (board, clues_count, success)
          - board: Modified board (will have changes if success=True)
          - clues_count: Number of clues in the returned board
          - success: Boolean indicating whether cells were removed
        """
        
        # Make a copy to avoid modifying the input board in case of failure
        board = [row[:] for row in current_board]
        
        # Identify cells that can be candidates for removal
        removal_candidates = [(r, c) for r, c in untried_positions 
                            if board[r][c] is not None]
        
        if not removal_candidates:
            return board, current_clues, False
            
        # Determine batch size - remove more cells when far from target
        batch_size = min(3, len(removal_candidates), current_clues - target_clues)
        batch_to_remove = random.sample(removal_candidates, batch_size)
        
        # Store original values in case we need to restore them
        original_values = [(r, c, board[r][c]) for r, c in batch_to_remove]
        
        # Remove the batch of cells
        for r, c in batch_to_remove:
            board[r][c] = None
            tried_positions.add((r, c))
        
        # Test if the puzzle still has a unique solution
        try:
            test_solver = cls(board, sub_grid_width, sub_grid_height)
            solutions = test_solver.find_all_solutions(max_solutions=2)
            
            if len(solutions) == 1:
                # Success - we can keep these cells removed
                return board, current_clues - batch_size, True
            else:
                # Not unique - restore all cells
                for r, c, val in original_values:
                    board[r][c] = val
                return board, current_clues, False
        except Exception:
            # On error, restore all values
            for r, c, val in original_values:
                board[r][c] = val
            return board, current_clues, False

    @classmethod
    def from_string(cls, sudoku_string, sub_grid_width=3, sub_grid_height=None, delimiter=None):
        """
        Create a SudokuMIPSolver instance from a string representation.
        
        Parameters:
        - sudoku_string: A string where each value represents a cell.
                         For boards ≤9x9: single characters (no delimiter needed)
                         For larger boards: values separated by delimiter
        - sub_grid_width: Width of the sub-grid (defaults to 3)
        - sub_grid_height: Height of the sub-grid (defaults to sub_grid_width)
        - delimiter: Character separating values (auto-detected if None)
        
        Returns:
        - A new SudokuMIPSolver instance
        
        Examples:
            # 9x9 board (single characters)
            "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
            
            # 16x16 board (space-separated)
            "1 2 0 0 5 6 0 0 9 10 0 0 13 14 0 0 3 4 0 0 7 8 0 0 11 12 0 0 15 16 0 0"
            
            # 16x16 board (comma-separated)
            "1,2,0,0,5,6,0,0,9,10,0,0,13,14,0,0,3,4,0,0,7,8,0,0,11,12,0,0,15,16,0,0"
        """
        if sub_grid_height is None:
            sub_grid_height = sub_grid_width
            
        size = sub_grid_width * sub_grid_height
        
        # Auto-detect delimiter if not provided
        if delimiter is None:
            if size <= 9:
                # For small boards, assume single character per cell
                delimiter = ""
            else:
                # For larger boards, detect common delimiters
                if "," in sudoku_string:
                    delimiter = ","
                elif " " in sudoku_string:
                    delimiter = " "
                else:
                    raise ValueError(f"For {size}x{size} boards, values must be separated by spaces or commas")
        
        # Parse based on delimiter
        if delimiter == "":
            # Single character mode (original behavior)
            sudoku_string = ''.join(sudoku_string.split())
            if len(sudoku_string) != size * size:
                raise ValueError(f"String length must be {size * size} for a {size}x{size} Sudoku")
            
            values = list(sudoku_string)
        else:
            # Delimited mode
            sudoku_string = sudoku_string.strip()
            values = sudoku_string.split(delimiter)
            if len(values) != size * size:
                raise ValueError(f"Must have exactly {size * size} values for a {size}x{size} Sudoku")
        
        # Parse values into board
        board = []
        for i in range(0, len(values), size):
            row = []
            for j in range(size):
                value_str = values[i + j].strip()
                
                # Convert to integer if valid
                if value_str.isdigit() and value_str != '0':
                    value = int(value_str)
                    if value > size:
                        raise ValueError(f"Value {value} is too large for {size}x{size} board")
                    row.append(value)
                else:
                    row.append(None)  # Empty cell (0, '.', or any non-digit)
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