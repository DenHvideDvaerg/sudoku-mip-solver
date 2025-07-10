"""
Sudoku MIP Solver - Command Line Interface

Provides command-line functionality for the Sudoku MIP Solver package.
"""
import argparse
import time
import sys
from sudoku_mip_solver import SudokuMIPSolver
from sudoku_mip_solver import __version__


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Solve Sudoku puzzles using Mixed Integer Programming"
    )
    
    # Version information
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # Input options
    # The default behavior (no input) generates AND solves a random puzzle
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-s", "--string", 
        help="Input puzzle as a string (e.g., '530070000600195000098000060800060003400803001700020006060000280000419005000080079')"
    )
    input_group.add_argument(
        "-f", "--file", 
        help="Path to a file containing the puzzle"
    )    

    # The --generate-only flag only generates a puzzle without solving it
    input_group.add_argument(
        "--generate-only",
        action="store_true",
        help="Generate a random puzzle without solving it"
    )
    
    # Grid dimensions
    grid_group = parser.add_argument_group("Grid Dimensions")
    grid_group.add_argument(
        "-w", "--width", 
        type=int, 
        default=3,
        help="Width of each sub-grid (default: 3)"
    )
    grid_group.add_argument(
        "-H", "--height", 
        type=int, 
        default=None,
        help="Height of each sub-grid (default: same as width)"
    )
    
    # Random puzzle options
    random_group = parser.add_argument_group("Random Puzzle Options")
    random_group.add_argument(
        "-d", "--difficulty", 
        type=float, 
        default=0.75,
        help="Controls number of clues in generated puzzles (0.0=maximum clues/easiest, 1.0=minimum clues/hardest, default: 0.75)"
    )
    random_group.add_argument(
        "--non-unique",
        action="store_true",
        help="Skip multiplicity check for random puzzles, allowing non-unique solutions (default: unique solutions)"
    )
    
    # Solver options
    solver_group = parser.add_argument_group("Solver Options")
    solver_group.add_argument(
        "-m", "--max-solutions", 
        type=int, 
        default=1,
        help="Maximum number of solutions to find (default: 1, use -1 for all solutions)"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o", "--output",
        help="Save the solution or generated puzzle to a file"
    )
    verbosity_group = output_group.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Show detailed solver information"
    )
    verbosity_group.add_argument(
        "-q", "--quiet",
        action="store_true", 
        help="Suppress all output except error messages"
    )

    return parser.parse_args()

def validate_arguments(args):
    """Validate parsed command line arguments."""
    if args.width <= 0:
        raise ValueError("--width must be a positive integer.")
    if args.height is not None and args.height <= 0:
        raise ValueError("--height must be a positive integer.")
    
    if not (0.0 <= args.difficulty <= 1.0):
        raise ValueError("--difficulty must be between 0.0 and 1.0.")

    if args.max_solutions < -1 or args.max_solutions == 0:
        raise ValueError("--max-solutions must be a positive integer or -1 for all solutions.")

def read_puzzle_from_file(filepath):
    """Read a Sudoku puzzle from a file."""
    try:
        with open(filepath, 'r') as file:
            return file.read().strip()
    except IOError as e:
        raise IOError(f"Error reading file '{filepath}': {e}") from e

def save_to_file(filepath, content, description):
    """Save content to a file with error handling."""
    try:
        with open(filepath, 'w') as file:
            file.write(content)
    except Exception as e:
        print(f"Error saving {description} to file '{filepath}': {e}", file=sys.stderr)

def generate_random_puzzle(args):
    """Generate a random puzzle with the provided arguments and display message."""
    if args.verbose:
        print(f"Generating random puzzle with target difficulty {args.difficulty}...")
    
    height = args.height if args.height is not None else args.width
    
    # Generate the random puzzle
    start_time = time.time()
    solver, actual_difficulty = SudokuMIPSolver.generate_random_puzzle(
        sub_grid_width=args.width,
        sub_grid_height=height,
        target_difficulty=args.difficulty,
        unique_solution=not args.non_unique
    )
    board = solver.board
    
    if args.verbose:
        generation_time = time.time() - start_time
        print(f"Puzzle generated in {generation_time:.4f} seconds")

    # Display the puzzle
    if not args.quiet:
        # Calculate and display puzzle difficulty information
        size = solver.size
        total_cells = size * size
        filled_cells = sum(1 for r in range(size) for c in range(size) if board[r][c] is not None)
        min_possible = max(1, size)
        
        if size == 9:
            min_possible = 17  # Known minimum for 9x9 Sudoku
            min_known = True
        else:
            min_known = False  # For other sizes, we don't know the true minimum
        
        # Calculate the difficulty we actually achieved as a percentage of theoretical maximum
        achievement_percentage = (actual_difficulty / 1.0) * 100
        
        print(f"Generated puzzle (difficulty: {actual_difficulty:.2f}, {filled_cells}/{total_cells} clues):")
        
        if min_known:
            print(f"[Min possible: {min_possible} clues (proven), " 
                  f"Achieved: {achievement_percentage:.1f}% of theoretical max]")
        else:
            print(f"[Min estimated: {min_possible} clues (lower bound), " 
                  f"Achieved: {achievement_percentage:.1f}% of theoretical max]")
        solver.pretty_print(board)
            
    return solver, board


def get_solver(args):
    """Initialize the Sudoku solver based on input arguments."""
    height = args.height if args.height is not None else args.width
    
    if args.string:
        if args.verbose:
            print("Using provided string as puzzle input...")
        solver = SudokuMIPSolver.from_string(args.string, args.width, height)
        if not args.quiet:
            print("Input puzzle:")
            solver.pretty_print(solver.board)
        return solver
    elif args.file:
        if args.verbose:
            print(f"Reading puzzle from file: {args.file}")
        puzzle_string = read_puzzle_from_file(args.file)
        solver = SudokuMIPSolver.from_string(puzzle_string, args.width, height)
        if not args.quiet:
            print("Puzzle from file:")
            solver.pretty_print(solver.board)
        return solver
    else:
        # Default: generate a random puzzle
        solver, _ = generate_random_puzzle(args)
        return solver


def save_solutions(solver, solutions, filepath):
    """Save one or more solutions to a file."""
    if len(solutions) == 1:
        content = solver.to_string(board=solutions[0])
        description = "solution"
    else:
        all_solutions_text = []
        for idx, solution in enumerate(solutions):
            all_solutions_text.append(f"Solution {idx + 1}:\n{solver.to_string(board=solution)}")
        content = "\n\n".join(all_solutions_text)
        description = "solutions"
    
    save_to_file(filepath, content, description)


def solve_and_report(solver, args):
    """Solve the puzzle and report the solution(s)."""
    solve_start = time.time()

    if args.verbose:
        if args.max_solutions == 1:
            print("Finding a single solution...")
        else:
            max_sols_str = 'all' if args.max_solutions == -1 else f'up to {args.max_solutions}'
            print(f"Finding {max_sols_str} solution(s)...")

    if args.max_solutions == 1:
        has_solution = solver.solve()
        solutions = [solver.current_solution] if has_solution else []
    else:
        max_sols = None if args.max_solutions == -1 else args.max_solutions
        solutions = solver.find_all_solutions(max_solutions=max_sols)

    solve_time = time.time() - solve_start

    if solutions:
        if args.verbose:
            if args.max_solutions == 1:
                print(f"Solution found in {solve_time:.4f} seconds:")
            else:
                print(f"Found {len(solutions)} solution(s) in {solve_time:.4f} seconds")
        
        if not args.quiet:
            if len(solutions) == 1:
                 solver.pretty_print(solutions[0])
            else:
                for idx, solution in enumerate(solutions):
                    print(f"\nSolution {idx + 1}:")
                    solver.pretty_print(solution)
        
        if args.output:
            save_solutions(solver, solutions, args.output)
    else:
        print("No solution found!", file=sys.stderr)


def main_generate_only(args):
    """Handle the --generate-only mode."""
    solver, board = generate_random_puzzle(args)
    if not args.quiet:
        print(solver.to_string(board=board))
    if args.output:
        save_to_file(args.output, solver.to_string(board=board), "generated puzzle")

def main():
    """Main entry point for the Sudoku solver."""
    try:
        args = parse_arguments()
        validate_arguments(args)
        
        start_time = time.time()

        if args.generate_only:
            main_generate_only(args)
        else:
            solver = get_solver(args)
            solve_and_report(solver, args)

        if args.verbose:
            total_time = time.time() - start_time
            print(f"\nTotal execution time: {total_time:.4f} seconds")

    except (ValueError, IOError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()