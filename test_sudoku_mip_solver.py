import pytest
from sudoku_mip_solver import SudokuMIPSolver


class TestSudokuMIPSolverInit:
    """Test cases for SudokuMIPSolver.__init__ method focusing on board validation."""

    def test_initialization_sets_attributes_correctly_9x9(self):
        """Test that initialization sets all attributes correctly."""
        board = [[None for _ in range(9)] for _ in range(9)]
        solver = SudokuMIPSolver(board, 3, 3)
        
        assert solver.sub_grid_width == 3
        assert solver.sub_grid_height == 3
        assert solver.size == 9
        assert solver.board == board
        assert solver.model is None
        assert solver.current_solution is None
        assert solver.cut_constraints == []

    def test_initialization_sets_attributes_correctly_6x6(self):
        """Test that initialization sets all attributes correctly for a 6x6 board."""
        board = [[None for _ in range(6)] for _ in range(6)]
        solver_2x3 = SudokuMIPSolver(board, 2, 3)
        
        assert solver_2x3.sub_grid_width == 2
        assert solver_2x3.sub_grid_height == 3
        assert solver_2x3.size == 6

        solver_3x2 = SudokuMIPSolver(board, 3, 2)
        assert solver_3x2.sub_grid_width == 3
        assert solver_3x2.sub_grid_height == 2
        assert solver_3x2.size == 6
        

    def test_default_sub_grid_height(self):
        """Test that sub_grid_height defaults to sub_grid_width when not provided."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2)
        assert solver.sub_grid_width == 2
        assert solver.sub_grid_height == 2
        assert solver.size == 4
    
    def test_invalid_sub_grid_width_zero(self):
        """Test that sub_grid_width of 0 raises ValueError."""
        board = [[1]]
        with pytest.raises(ValueError, match="Sub-grid width must be at least 1"):
            SudokuMIPSolver(board, 0)
    
    def test_invalid_sub_grid_width_negative(self):
        """Test that negative sub_grid_width raises ValueError."""
        board = [[1]]
        with pytest.raises(ValueError, match="Sub-grid width must be at least 1"):
            SudokuMIPSolver(board, -1)
    
    def test_invalid_sub_grid_height_zero(self):
        """Test that sub_grid_height of 0 raises ValueError."""
        board = [[1]]
        with pytest.raises(ValueError, match="Sub-grid height must be at least 1"):
            SudokuMIPSolver(board, 1, 0)
    
    def test_invalid_sub_grid_height_negative(self):
        """Test that negative sub_grid_height raises ValueError."""
        board = [[1]]
        with pytest.raises(ValueError, match="Sub-grid height must be at least 1"):
            SudokuMIPSolver(board, 1, -1)
    
    def test_empty_board(self):
        """Test that empty board raises ValueError."""
        with pytest.raises(ValueError, match="Board must have exactly 4 rows"):
            SudokuMIPSolver([], 2, 2)
    
    def test_wrong_number_of_rows(self):
        """Test that incorrect number of rows raises ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, None],
            # Missing 2 rows for a 2x2 sub-grid (should be 4x4)
        ]
        with pytest.raises(ValueError, match="Board must have exactly 4 rows"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_inconsistent_row_lengths(self):
        """Test that inconsistent row lengths raise ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None],  # Too short
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Row 1 has 2 elements, should have 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_invalid_cell_value_too_large(self):
        """Test that cell values larger than board size raise ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, 5],  # 5 is too large for 4x4 board
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Invalid value 5 at position \\(1,3\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_invalid_cell_value_zero(self):
        """Test that cell value of 0 raises ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, 0],  # 0 is invalid
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Invalid value 0 at position \\(1,3\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_invalid_cell_value_negative(self):
        """Test that negative cell values raise ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, -1],  # Negative is invalid
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Invalid value -1 at position \\(1,3\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_invalid_cell_value_string(self):
        """Test that string cell values raise ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, "5"],  # String is invalid
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Invalid value 5 at position \\(1,3\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_invalid_cell_value_float(self):
        """Test that float cell values raise ValueError."""
        board = [
            [1, 2, 3, 4],
            [None, None, None, 3.5],  # Float is invalid
            [None, None, None, None],
            [None, None, None, None]
        ]
        with pytest.raises(ValueError, match="Invalid value 3.5 at position \\(1,3\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver(board, 2, 2)
    
    def test_valid_all_none_board(self):
        """Test that a board with all None values is valid."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2, 2)
        assert solver.size == 4
        assert all(all(cell is None for cell in row) for row in solver.board)