"""
Sudoku MIP Solver - A Mixed Integer Programming approach to solving and generating Sudoku puzzles.

This package provides tools to:
- Solve Sudoku puzzles of any size using MIP optimization techniques
- Generate random Sudoku puzzles with varying difficulty levels
- Find all possible solutions for a given puzzle
- Support non-standard Sudoku grid dimensions (e.g., 12x12 with 4x3 sub-grids)
"""

from .sudoku_mip_solver import SudokuMIPSolver

__version__ = "0.1.0"
__all__ = ["SudokuMIPSolver"]
