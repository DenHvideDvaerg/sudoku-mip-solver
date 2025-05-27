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


class TestSudokuMIPSolverFromString:
    """Test cases for SudokuMIPSolver.from_string class method."""
    
    def test_from_string_standard_9x9(self):
        """Test creating a 9x9 Sudoku from string with default 3x3 sub-grids."""
        sudoku_string = "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
        solver = SudokuMIPSolver.from_string(sudoku_string)
        
        assert solver.size == 9
        assert solver.sub_grid_width == 3
        assert solver.sub_grid_height == 3
        
        # Check specific values from the string
        assert solver.board[0][0] == 7
        assert solver.board[0][1] is None  # '0' should become None
        assert solver.board[0][5] == 6
        assert solver.board[8][8] == 3
    
    def test_from_string_with_dots(self):
        """Test string parsing with dots for empty cells."""
        sudoku_string = "7....62...8...1..7.46.7.3...6..9.....5..4..2.....1..4...9.2.57.5..1...8...89....3"  # 81 chars
        solver = SudokuMIPSolver.from_string(sudoku_string)
        
        assert solver.size == 9
        assert solver.board[0][0] == 7
        assert solver.board[0][1] is None  # '.' should become None
        assert solver.board[0][5] == 6
        assert solver.board[8][8] == 3

    def test_from_string_4x4_with_2x2_subgrids(self):
        """Test creating a 4x4 Sudoku from string with 2x2 sub-grids."""
        sudoku_string = "1003200040010000"
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        
        assert solver.size == 4
        assert solver.sub_grid_width == 2
        assert solver.sub_grid_height == 2
        
        expected_board = [
            [1, None, None, 3],
            [2, None, None, None],
            [4, None, None, 1],
            [None, None, None, None]
        ]
        assert solver.board == expected_board
    
    def test_from_string_6x6_with_3x2_subgrids(self):
        """Test creating a 6x6 Sudoku from string with 3x2 sub-grids."""
        sudoku_string = "123456000000000000000000000000000000"
        solver = SudokuMIPSolver.from_string(sudoku_string, 3, 2)
        
        assert solver.size == 6
        assert solver.sub_grid_width == 3
        assert solver.sub_grid_height == 2
        
        # First row should have 1,2,3,4,5,6
        assert solver.board[0] == [1, 2, 3, 4, 5, 6]
        # Rest should be None
        for r in range(1, 6):
            assert all(cell is None for cell in solver.board[r])
    
    def test_from_string_6x6_with_2x3_subgrids(self):
        """Test creating a 6x6 Sudoku from string with 2x3 sub-grids."""
        sudoku_string = "120000300000000000000000000000000000"
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 3)
        
        assert solver.size == 6
        assert solver.sub_grid_width == 2
        assert solver.sub_grid_height == 3
        
        expected_first_row = [1, 2, None, None, None, None]
        expected_second_row = [3, None, None, None, None, None]
        assert solver.board[0] == expected_first_row
        assert solver.board[1] == expected_second_row
    
    def test_from_string_default_sub_grid_height(self):
        """Test that sub_grid_height defaults to sub_grid_width."""
        sudoku_string = "1000200030004000"
        solver = SudokuMIPSolver.from_string(sudoku_string, 2)  # Only width provided
        
        assert solver.sub_grid_width == 2
        assert solver.sub_grid_height == 2  # Should default to width
        assert solver.size == 4
    
    def test_from_string_with_mixed_empty_chars(self):
        """Test string parsing with various characters for empty cells."""
        sudoku_string = "1.2x3_4-abcd0000"  # 16 chars for 4x4 grid with various empty cell representations
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        
        expected_board = [
            [1, None, 2, None],
            [3, None, 4, None],
            [None, None, None, None],  # Non-digits become None
            [None, None, None, None]   # Zeros become None
        ]
        assert solver.board == expected_board
    
    def test_from_string_with_whitespace(self):
        """Test that whitespace is properly removed from input string."""
        sudoku_string = """1 2 3 4
                          0 0 0 0
                          0 0 0 0  
                          0 0 0 0"""
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        
        expected_first_row = [1, 2, 3, 4]
        assert solver.board[0] == expected_first_row
        # Rest should be None (zeros become None)
        for r in range(1, 4):
            assert all(cell is None for cell in solver.board[r])
    
    def test_from_string_invalid_length_too_short(self):
        """Test that string too short for board size raises ValueError."""
        sudoku_string = "123"  # Too short for 4x4 board (needs 16)
        with pytest.raises(ValueError, match="String length must be 16 for a 4x4 Sudoku"):
            SudokuMIPSolver.from_string(sudoku_string, 2, 2)
    
    def test_from_string_invalid_length_too_long(self):
        """Test that string too long for board size raises ValueError."""
        sudoku_string = "12345678901234567"  # Too long for 4x4 board (needs 16)
        with pytest.raises(ValueError, match="String length must be 16 for a 4x4 Sudoku"):
            SudokuMIPSolver.from_string(sudoku_string, 2, 2)
    
    def test_from_string_with_invalid_digits(self):
        """Test string with digits larger than board size."""
        # For 4x4 board, valid digits are 1-4, but string contains '5'
        sudoku_string = "1234567890123456"
        with pytest.raises(ValueError, match="Invalid value 5 at position \\(1,0\\). Must be None or integer from 1 to 4"):
            SudokuMIPSolver.from_string(sudoku_string, 2, 2)
    
    def test_from_string_empty_string(self):
        """Test behavior with empty string."""
        with pytest.raises(ValueError, match="String length must be 4 for a 2x2 Sudoku"):
            SudokuMIPSolver.from_string("", 1, 2)
    
    def test_from_string_all_empty_cells(self):
        """Test string with all empty cells."""
        sudoku_string = "................"  # 16 dots for 4x4
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        
        # All cells should be None
        for row in solver.board:
            assert all(cell is None for cell in row)
    
    def test_from_string_all_filled_cells(self):
        """Test string with all cells filled (valid puzzle)."""
        # Valid 4x4 Sudoku solution
        sudoku_string = "1234341221434321"
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        
        expected_board = [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [2, 1, 4, 3],
            [4, 3, 2, 1]
        ]
        assert solver.board == expected_board

    def test_from_string_large_digits_for_big_board(self):
        """Test string parsing for larger boards with double-digit sizes."""
        # For a 4x3 = 12 size board, valid digits are 1-9 and 10,11,12
        # But since we parse character by character, this is limited to single digits
        # This test shows the limitation - we can only handle sizes up to 9
        sudoku_string = "123456789" * 16  # 144 chars for 12x12, but only uses digits 1-9
        
        # This should work since all digits 1-9 are valid for a 12x12 board
        solver = SudokuMIPSolver.from_string(sudoku_string, 4, 3)
        assert solver.size == 12
        assert all(1 <= cell <= 9 for row in solver.board for cell in row if cell is not None)

    # TODO: update from_string to handle multi-digit input for boards bigger than 9x9