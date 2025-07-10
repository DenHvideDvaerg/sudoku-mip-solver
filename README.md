# Sudoku MIP Solver

[![CI](https://github.com/DenHvideDvaerg/sudoku-mip-solver/actions/workflows/CI.yml/badge.svg)](https://github.com/DenHvideDvaerg/sudoku-mip-solver/actions/workflows/CI.yml)
[![Code Coverage](https://img.shields.io/badge/Code%20Coverage-see%20workflow-informational)](https://github.com/DenHvideDvaerg/sudoku-mip-solver/actions/workflows/CI.yml)
[![PyPI version](https://badge.fury.io/py/sudoku-mip-solver.svg)](https://pypi.org/project/sudoku-mip-solver/)

A Sudoku puzzle solver and generator using Mixed Integer Programming (MIP).

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Command Line Interface](#command-line-interface)
- [SudokuMIPSolver API](#sudokumipsolver-api)
- [Examples](#examples)
- [License](#license)

## Features

This package provides tools to:
- Solve Sudoku puzzles of any size using MIP optimization techniques
- Generate random Sudoku puzzles with varying difficulty levels
- Find all possible solutions for a given puzzle
- Support non-standard Sudoku grid dimensions (e.g., 12x12 with 4x3 sub-grids)

## Installation

```bash
pip install sudoku-mip-solver
```

## Requirements

- Python 3.9+
- PuLP (for the MIP solver)

## Quick Start

```python
from sudoku_mip_solver import SudokuMIPSolver

# Create a solver from a string representation of a 9x9 puzzle
puzzle_string = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
solver = SudokuMIPSolver.from_string(puzzle_string)

# Solve the puzzle
if solver.solve():
    solver.pretty_print(solver.get_solution())
else:
    print("No solution found!")
    
# Generate a random puzzle
new_solver, difficulty = SudokuMIPSolver.generate_random_puzzle(
    sub_grid_width=3,
    sub_grid_height=3,
    target_difficulty=0.75
)
print(f"Generated puzzle with difficulty {difficulty:.2f}:")
new_solver.pretty_print(new_solver.board)
```

## Command Line Interface

The package includes a command-line interface for solving and generating puzzles.

### Basic Usage

```bash
# Display the version of the package
sudoku-mip-solver --version

# Solve a puzzle provided as a string
sudoku-mip-solver -s "530070000600195000098000060800060003400803001700020006060000280000419005000080079"

# Read a puzzle from a file
sudoku-mip-solver -f puzzle.txt

# Generate a random puzzle with medium difficulty
sudoku-mip-solver

# Generate but don't solve a puzzle
sudoku-mip-solver --generate-only

# Find all solutions to a puzzle
sudoku-mip-solver -f puzzle.txt -m -1

# Solve a non-standard 6x6 puzzle (2x3 sub-grids)
sudoku-mip-solver -s "530070600195098000" -w 2 -H 3
```

### Command Line Options

#### Input Options

| Option | Description |
| ------ | ----------- |
| `-s`, `--string` | Input puzzle as a string |
| `-f`, `--file` | Path to a file containing the puzzle |
| `--generate-only` | Generate a random puzzle without solving it |

#### Grid Dimensions

| Option | Description |
| ------ | ----------- |
| `-w`, `--width` | Width of each sub-grid (default: 3) |
| `-H`, `--height` | Height of each sub-grid (default: same as width) |

#### Random Puzzle Options

| Option | Description |
| ------ | ----------- |
| `-d`, `--difficulty` | Controls number of clues (0.0=easiest, 1.0=hardest, default: 0.75) |
| `--non-unique` | Skip uniqueness check, allowing multiple solutions |

#### Solver Options

| Option | Description |
| ------ | ----------- |
| `-m`, `--max-solutions` | Maximum solutions to find (default: 1, use -1 for all) |

#### Output Options

| Option | Description |
| ------ | ----------- |
| `-o`, `--output` | Save the solution or generated puzzle to a file |
| `-v`, `--verbose` | Show detailed solver information |
| `-q`, `--quiet` | Suppress all output except error messages |
| `--version` | Display the version number of the package |

## SudokuMIPSolver API

### Creating a Solver

```python
# From a 2D array
board = [[5,3,0,0,7,0,0,0,0], 
         [6,0,0,1,9,5,0,0,0],
         # ... (additional rows)
        ]
solver = SudokuMIPSolver(board, sub_grid_width=3, sub_grid_height=3)

# From a string representation
solver = SudokuMIPSolver.from_string("530070000...", sub_grid_width=3)

# Generate a random puzzle
solver, difficulty = SudokuMIPSolver.generate_random_puzzle(
    sub_grid_width=3,
    sub_grid_height=3,
    target_difficulty=0.75,
    unique_solution=True
)
```

### Core Methods

| Method | Description |
| ------ | ----------- |
| `build_model()` | Build the MIP model with all Sudoku constraints |
| `solve(show_output=False)` | Solve the puzzle and return True if solution found |
| `find_all_solutions(max_solutions=None)` | Find all solutions (or up to max_solutions) |
| `get_solution()` | Get the current solution |
| `reset_model()` | Remove all solution cuts, restoring original constraints |

### Utility Methods

| Method | Description |
| ------ | ----------- |
| `to_string(board=None, delimiter=None)` | Convert board to string representation |
| `pretty_print(board=None)` | Print the board with grid lines showing sub-grids |
| `extract_solution()` | Extract solution from model variables |
| `print_model()` | Print the model in a readable format |

### Class Methods

| Method | Description |
| ------ | ----------- |
| `from_string(sudoku_string, sub_grid_width=3, sub_grid_height=None, delimiter=None)` | Create solver from string representation |
| `generate_random_puzzle(sub_grid_width=3, sub_grid_height=None, target_difficulty=0.75, unique_solution=True, max_attempts=100, random_seed=None)` | Generate a random puzzle with specified parameters |

### Algorithm Details

The solver uses Mixed Integer Programming (MIP) to model and solve Sudoku puzzles:

1. **Decision Variables**: Binary variables x[i,j,k] representing whether cell (i,j) contains value k
2. **Constraints**:
   - Each cell must contain exactly one value
   - Each row must contain all values exactly once
   - Each column must contain all values exactly once
   - Each sub-grid must contain all values exactly once
   - Initial clues are fixed to their given values
3. **Solution Finding**: 
   - The MIP solver (provided by PuLP) finds a feasible solution satisfying all constraints
   - For multiple solutions, solution cuts are added to exclude previously found solutions

The random puzzle generator works by:
1. Creating a complete, solved Sudoku grid
2. Systematically removing values while ensuring the puzzle maintains a unique solution
3. Continuing removal until the target difficulty level is reached

## Examples

### Solving a Puzzle

```python
# Standard 9x9 puzzle
puzzle = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
solver = SudokuMIPSolver.from_string(puzzle)
solver.solve()
solver.pretty_print(solver.get_solution())
```

### Finding Multiple Solutions

```python
# Find all solutions to an under-constrained puzzle
puzzle = "123456789000000000000000000000000000000000000000000000000000000000000000000000000"
solver = SudokuMIPSolver.from_string(puzzle)
solutions = solver.find_all_solutions(max_solutions=5)  # Limit to 5 solutions
print(f"Found {len(solutions)} solutions")
```

### Working with Non-Standard Grids

```python
# Create a 6x6 puzzle with 2x3 sub-grids
puzzle = "123456000000000000000000000000000000"
solver = SudokuMIPSolver.from_string(puzzle, sub_grid_width=2, sub_grid_height=3)
solver.solve()
solver.pretty_print(solver.get_solution())
```

### Generating Puzzles with Different Difficulties

The `target_difficulty` parameter controls the number of clues in the generated puzzle:
- 0.0 = maximum clues (easiest puzzles)
- 1.0 = minimum clues (hardest puzzles)

For standard 9×9 Sudoku puzzles, a difficulty of 1.0 targets the theoretical minimum of 17 clues (mathematically proven lower bound). For puzzles of other sizes, the minimum is (wrongly) estimated as N clues for an N×N grid.

```python
# Very easy puzzle (more clues)
easy_solver, difficulty = SudokuMIPSolver.generate_random_puzzle(target_difficulty=0.3)
print(f"Easy puzzle (difficulty: {difficulty:.2f})")
easy_solver.pretty_print(easy_solver.board)

# Harder puzzle (fewer clues)
hard_solver, difficulty = SudokuMIPSolver.generate_random_puzzle(target_difficulty=0.9)
print(f"Hard puzzle (difficulty: {difficulty:.2f})")
hard_solver.pretty_print(hard_solver.board)
```

## License

This project is licensed under the [MIT License](LICENSE).