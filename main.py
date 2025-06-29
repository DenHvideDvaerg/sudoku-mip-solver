#!/usr/bin/env python3
"""
Sudoku MIP Solver - Command Line Interface

A tool for solving Sudoku puzzles using Mixed Integer Programming (MIP).
"""
import argparse
import time
import sys
from sudoku_mip_solver import SudokuMIPSolver


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Solve Sudoku puzzles using Mixed Integer Programming"
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
        "-ht", "--height", 
        type=int, 
        default=None,
        help="Height of each sub-grid (default: same as width)"
    )
    
    # Random puzzle options
    random_group = parser.add_argument_group("Random Puzzle Options")
    random_group.add_argument(
        "-d", "--difficulty", 
        type=float, 
        default=0.5,
        help="Difficulty of random puzzles (0.0-1.0, default: 0.5)"
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
        "-v", "--verbose", 
        action="store_true",
        help="Show detailed solver information"
    )

    return parser.parse_args()

def read_puzzle_from_file(filepath):
    """Read a Sudoku puzzle from a file."""
    try:
        with open(filepath, 'r') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

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
    print(f"Generated puzzle (actual difficulty: {actual_difficulty:.2f}):")
    solver.pretty_print(board)
            
    return solver, board

def main():
    """Main entry point for the Sudoku solver."""
    args = parse_arguments()
    
    start_time = time.time()
    
    # Determine puzzle source and create the board
    if args.generate_only:
        solver, board = generate_random_puzzle(args)
        print(solver.to_string(board=board))
        if args.verbose:
            total_time = time.time() - start_time
            print(f"\nTotal execution time: {total_time:.4f} seconds")
        return  # Exit function without solving
    elif args.string:
        if args.verbose:
            print("Using provided string as puzzle input...")
        height = args.height if args.height is not None else args.width
        try:
            solver = SudokuMIPSolver.from_string(args.string, args.width, height)
            board = solver.board
            print("Input puzzle:")
            solver.pretty_print(board)
        except Exception as e:
            print(f"Error parsing puzzle string: {e}")
            sys.exit(1)
    elif args.file:
        if args.verbose:
            print(f"Reading puzzle from file: {args.file}")
        puzzle_string = read_puzzle_from_file(args.file)
        height = args.height if args.height is not None else args.width
        try:
            solver = SudokuMIPSolver.from_string(puzzle_string, args.width, height)
            board = solver.board
            print("Puzzle from file:")
            solver.pretty_print(board)
        except Exception as e:
            print(f"Error parsing puzzle from file: {e}")
            sys.exit(1)
    else:
        # Default: generate a random puzzle
        solver, board = generate_random_puzzle(args)
        
    if 'solver' not in locals():
        raise RuntimeError("Internal error: solver not initialized")
    
    # Find one or more solutions based on max_solutions
    if args.max_solutions == 1:
        # Find a single solution
        if args.verbose:
            print("Finding a single solution...")
            
        solve_start = time.time()
        has_solution = solver.solve()
        solve_time = time.time() - solve_start
        
        if has_solution:
            if args.verbose:
                print(f"Solution found in {solve_time:.4f} seconds:")
            solver.pretty_print(solver.current_solution)
        else:
            print("No solution found!")
    else:
        # Find multiple or all solutions
        max_sols = None if args.max_solutions == -1 else args.max_solutions
        
        if args.verbose:
            print(f"Finding {'all' if max_sols is None else f'up to {max_sols}'} solution(s)...")
        
        solve_start = time.time()
        all_solutions = solver.find_all_solutions(max_solutions=max_sols)
        solve_time = time.time() - solve_start
        
        if all_solutions:
            if args.verbose:
                print(f"Found {len(all_solutions)} solution(s) in {solve_time:.4f} seconds")

            for idx, solution in enumerate(all_solutions):
                print(f"\nSolution {idx + 1}:")
                solver.pretty_print(solution)
        else:
            print("No solutions found!")
    
    
    if args.verbose:
        total_time = time.time() - start_time
        print(f"\nTotal execution time: {total_time:.4f} seconds")


if __name__ == "__main__":
    main()