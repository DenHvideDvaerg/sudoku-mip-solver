import pytest
from pulp import LpInteger
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
    
    def test_from_string_whitespace(self):
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
        with pytest.raises(ValueError, match="Value 5 is too large for 4x4 board"):
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
        """Test string parsing for larger boards requires delimiters."""
        # For a 4x3 = 12 size board, delimiter is required since size > 9
        sudoku_string = "123456789" * 16  # 144 chars for 12x12, but no delimiters
        
        # This should fail since 12x12 boards require delimiters
        with pytest.raises(ValueError, match="For 12x12 boards, values must be separated by spaces or commas"):
            SudokuMIPSolver.from_string(sudoku_string, 4, 3)

    # Enhanced tests for delimiter-based parsing (multi-digit support)
    
    def test_from_string_16x16_space_delimited(self):
        """Test creating a 16x16 Sudoku from space-delimited string."""
        # Create a partial 16x16 puzzle with space-separated values
        values = ["1", "2", "0", "0", "5", "6", "0", "0", "9", "10", "0", "0", "13", "14", "0", "0"] * 16
        sudoku_string = " ".join(values)
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 4, 4)
        
        assert solver.size == 16
        assert solver.sub_grid_width == 4
        assert solver.sub_grid_height == 4
        
        # Check specific values
        assert solver.board[0][0] == 1
        assert solver.board[0][1] == 2
        assert solver.board[0][2] is None  # '0' becomes None
        assert solver.board[0][8] == 9
        assert solver.board[0][9] == 10
    
    def test_from_string_16x16_comma_delimited(self):
        """Test creating a 16x16 Sudoku from comma-delimited string."""
        # Create pattern with comma separation
        values = ["0"] * 256  # All empty cells
        values[0] = "16"  # First cell
        values[17] = "15"  # Second row, second cell
        values[255] = "1"  # Last cell
        
        sudoku_string = ",".join(values)
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 4, 4)
        
        assert solver.size == 16
        assert solver.board[0][0] == 16
        assert solver.board[1][1] == 15
        assert solver.board[15][15] == 1
        # Most cells should be None
        none_count = sum(1 for row in solver.board for cell in row if cell is None)
        assert none_count == 253  # 256 - 3 filled cells
    
    def test_from_string_auto_detect_space_delimiter(self):
        """Test auto-detection of space delimiter for large boards."""
        # 10x10 board requires delimiter since size > 9
        values = ["1", "10", "0", "5"] + ["0"] * 96  # 100 values total
        sudoku_string = " ".join(values)
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 5, 2)  # 5x2 sub-grids
        
        assert solver.size == 10
        assert solver.board[0][0] == 1
        assert solver.board[0][1] == 10
        assert solver.board[0][2] is None
        assert solver.board[0][3] == 5
    
    def test_from_string_auto_detect_comma_delimiter(self):
        """Test auto-detection of comma delimiter for large boards."""
        values = ["12", "0", "11", "0"] + ["0"] * 140  # 144 values for 12x12
        sudoku_string = ",".join(values)
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 3, 4)  # 3x4 sub-grids
        
        assert solver.size == 12
        assert solver.board[0][0] == 12
        assert solver.board[0][1] is None
        assert solver.board[0][2] == 11
        assert solver.board[0][3] is None
    
    def test_from_string_explicit_delimiter_parameter(self):
        """Test explicit delimiter parameter override."""
        # Use semicolon as delimiter
        values = ["1", "2", "0", "4"] + ["0"] * 12  # 16 values for 4x4
        sudoku_string = ";".join(values)
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2, delimiter=";")
        
        assert solver.size == 4
        assert solver.board[0] == [1, 2, None, 4]
    
    def test_from_string_delimiter_detection_error(self):
        """Test error when no delimiter can be detected for large boards."""
        # 10x10 board without spaces or commas
        sudoku_string = "1234567890" * 10  # 100 chars but no delimiters
        
        with pytest.raises(ValueError, match="For 10x10 boards, values must be separated by spaces or commas"):
            SudokuMIPSolver.from_string(sudoku_string, 5, 2)
    
    def test_from_string_wrong_number_of_delimited_values(self):
        """Test error for wrong number of delimited values."""
        # 10x10 board needs 100 values, but provide only 99 (forces delimiter mode)
        values = ["1", "2", "0"] * 33  # 99 values, need 100
        sudoku_string = " ".join(values)
        
        with pytest.raises(ValueError, match="Must have exactly 100 values for a 10x10 Sudoku"):
            SudokuMIPSolver.from_string(sudoku_string, 5, 2)
    
    def test_from_string_whitespace_handling_delimited(self):
        """Test proper whitespace handling in delimited strings."""        
        values = ["1", "2", "0", "4"] + ["0"] * 12
        sudoku_string = "  " + " ,  ".join(values) + "  "
        
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2, delimiter=",")
        
        assert solver.size == 4
        assert solver.board[0] == [1, 2, None, 4]

class TestSudokuMIPSolverToString:
    """Test cases for the to_string method."""

    def test_to_string_9x9_no_delimiter(self):
        """Test converting a 9x9 board to a string without a delimiter."""
        sudoku_string = "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
        solver = SudokuMIPSolver.from_string(sudoku_string)
        assert solver.to_string() == sudoku_string

    def test_to_string_4x4_with_delimiter(self):
        """Test converting a 4x4 board with a specified delimiter."""
        sudoku_string = "1003200040010000"
        solver = SudokuMIPSolver.from_string(sudoku_string, 2, 2)
        expected_string = "1,0,0,3,2,0,0,0,4,0,0,1,0,0,0,0"
        assert solver.to_string(delimiter=",") == expected_string

    def test_to_string_on_solution(self):
        """Test converting a solution board to a string."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2)
        solution_board = [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [2, 1, 4, 3],
            [4, 3, 2, 1]
        ]
        solver.current_solution = solution_board
        expected_string = "1234341221434321"
        assert solver.to_string(board=solver.current_solution) == expected_string


class TestSudokuMIPSolverBuildModel:
    """Test cases for SudokuMIPSolver.build_model method."""
    
    def test_model_creation(self):
        """Test that the model is created with correct structure."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2, 2)
        model = solver.build_model()
        
        # Verify model was created
        assert model is not None
        assert solver.model is not None
        assert model is solver.model
        
        # Verify objective is dummy (value 0)
        assert model.objective.value() == 0
    
    def test_variables_creation_4x4(self):
        """Test that variables are created correctly for a 4x4 board."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2, 2)
        solver.build_model()
        
        # Should have r*c*v variables = 4*4*4 = 64 variables
        assert len(solver.variables) == 64
        
        # Check specific variable exists with correct attributes
        var = solver.variables[0, 0, 1]  # Top-left cell, value 1
        assert var.name == "x_(1,1,1)"
        assert var.lowBound == 0
        assert var.upBound == 1
        assert var.cat == LpInteger # Binary variables are simply integer variables bounded between 0 and 1
    
    def test_constraint_counts_4x4(self):
        """Test that the right number of constraints are created for 4x4 board."""
        board = [[None for _ in range(4)] for _ in range(4)]
        solver = SudokuMIPSolver(board, 2, 2)
        model = solver.build_model()
        
        # Calculate expected constraints:
        # - One value per cell: 4×4 = 16 constraints
        # - One of each value per row: 4×4 = 16 constraints
        # - One of each value per column: 4×4 = 16 constraints
        # - One of each value per box: 2×2×4 = 16 constraints
        # - No initial values in this example
        # Total: 64 constraints
        
        assert len(model.constraints) == 64
        
        # Verify constraint names by type
        cell_constraints = [c for c in model.constraints if c.startswith("cell_")]
        row_constraints = [c for c in model.constraints if c.startswith("row_")]
        col_constraints = [c for c in model.constraints if c.startswith("col_")]
        box_constraints = [c for c in model.constraints if c.startswith("box_")]
        fixed_constraints = [c for c in model.constraints if c.startswith("fixed_value")]
        
        assert len(cell_constraints) == 16
        assert len(row_constraints) == 16
        assert len(col_constraints) == 16
        assert len(box_constraints) == 16
        assert len(fixed_constraints) == 0  # No initial values
    
    def test_constraint_counts_9x9(self):
        """Test that the right number of constraints are created for 9x9 board."""
        board = [[None for _ in range(9)] for _ in range(9)]
        # Fill a few cells with values
        board[0][0] = 5
        board[1][2] = 3
        board[8][8] = 1
        
        solver = SudokuMIPSolver(board, 3, 3)
        model = solver.build_model()
        
        # Calculate expected constraints:
        # - One value per cell: 9×9 = 81 constraints
        # - One of each value per row: 9×9 = 81 constraints
        # - One of each value per column: 9×9 = 81 constraints
        # - One of each value per box: 3×3×9 = 81 constraints
        # - Fixed values: 3 constraints
        # Total: 327 constraints
        
        assert len(model.constraints) == 327
        
        # Verify constraint names by type
        cell_constraints = [c for c in model.constraints if c.startswith("cell_")]
        row_constraints = [c for c in model.constraints if c.startswith("row_")]
        col_constraints = [c for c in model.constraints if c.startswith("col_")]
        box_constraints = [c for c in model.constraints if c.startswith("box_")]
        fixed_constraints = [c for c in model.constraints if c.startswith("fixed_value")]
        
        assert len(cell_constraints) == 81
        assert len(row_constraints) == 81
        assert len(col_constraints) == 81
        assert len(box_constraints) == 81
        assert len(fixed_constraints) == 3
    
    def test_fixed_values_constraints(self):
        """Test that initial values are properly fixed in the model."""
        # Create a board with some initial values
        board = [
            [1, None, 3, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, 4, None, 2]
        ]
        solver = SudokuMIPSolver(board, 2, 2)
        solver.build_model()
        
        # Check that the right variables are fixed to 1
        # These constraints fix initial values
        # Note: the constant in the constraint is -1 for fixed values (on the left side of the equation)
        constraints = solver.model.constraints
        
        # Check value 1 at position (0,0)
        assert "fixed_value_at_1_1" in constraints
        constraint = constraints["fixed_value_at_1_1"]
        # Should be "x_(1,1,1) = 1"
        assert constraint.constant == -1
        
        # Check value 3 at position (0,2)
        assert "fixed_value_at_1_3" in constraints
        constraint = constraints["fixed_value_at_1_3"]
        # Should be "x_(1,3,3) = 1"
        assert constraint.constant == -1
        
        # Check value 4 at position (3,1)
        assert "fixed_value_at_4_2" in constraints
        constraint = constraints["fixed_value_at_4_2"]
        # Should be "x_(4,2,4) = 1" 
        assert constraint.constant == -1
        
        # Check value 2 at position (3,3)
        assert "fixed_value_at_4_4" in constraints
        constraint = constraints["fixed_value_at_4_4"]
        # Should be "x_(4,4,2) = 1"
        assert constraint.constant == -1
    
    def test_build_model_complex_shape(self):
        """Test building model with non-square sub-grids (6x6 with 2x3 sub-grids)."""
        board = [[None for _ in range(6)] for _ in range(6)]
        solver = SudokuMIPSolver(board, 2, 3)
        model = solver.build_model()
        
        # Calculate expected constraints:
        # - One value per cell: 6×6 = 36 constraints
        # - One of each value per row: 6×6 = 36 constraints
        # - One of each value per column: 6×6 = 36 constraints
        # - One of each value per box: 3×2×6 = 36 constraints
        # Total: 144 constraints
        
        assert len(model.constraints) == 144
        
        # Verify box constraint structure by checking a few boxes
        # For 2x3 sub-grids, we should have 2 rows of boxes and 3 columns of boxes
        box_constraints = {c: model.constraints[c] for c in model.constraints if c.startswith("box_")}
        
        # Check that we have constraints for all box coordinates
        # For 2x3 sub-grids in a 6x6 board, we have:
        # - Boxes in rows: 6÷3 = 2 rows (indexed 1-2 in constraint names)
        # - Boxes in columns: 6÷2 = 3 columns (indexed 1-3 in constraint names)
        for box_r in range(1, 3):  # 2 rows of boxes (1-based indexing in names)
            for box_c in range(1, 4):  # 3 columns of boxes
                for v in range(1, 7):  # 6 values
                    constraint_name = f"box_{box_r}_{box_c}_has_value_{v}"
                    assert constraint_name in box_constraints, f"Missing constraint: {constraint_name}"

class TestSudokuMIPSolverSolve:
    """Test cases for SudokuMIPSolver solving methods."""
    
    @classmethod
    def validate_4x4_solution(cls, solution):
        expected_values = set(range(1, 5))  
         
        # Check rows
        for r in range(4):
            row_values = set(solution[r][c] for c in range(4))
            assert row_values == expected_values, f"Row {r+1} has invalid values: {row_values}"

        # Check columns
        for c in range(4):
            col_values = set(solution[r][c] for r in range(4))
            assert col_values == expected_values, f"Column {c+1} has invalid values: {col_values}"

        # Check sub-grids
        for box_r in range(2):  # 2 rows of boxes
            for box_c in range(2):  # 2 columns of boxes
                 box_values = set(solution[box_r*2 + r][box_c*2 + c] 
                             for r in range(2) for c in range(2))
            assert box_values == expected_values, f"Box ({box_r+1},{box_c+1}) has invalid values: {box_values}"

    def test_solve_basic_4x4(self):
        """Test solving a very simple 4x4 sudoku puzzle."""
        # Create a 4x4 board with some initial values
        board = [
            [1, None, None, 4],
            [None, 4, 1, None],
            [4, 1, None, None],
            [None, None, 4, 1]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        result = solver.solve()
        
        assert result is True
        assert solver.current_solution is not None
        
        solution = solver.current_solution
        # Verify initial values are preserved
        assert solution[0][0] == 1
        assert solution[0][3] == 4
        assert solution[1][1] == 4
        assert solution[1][2] == 1
        assert solution[2][0] == 4
        assert solution[2][1] == 1
        assert solution[3][2] == 4
        assert solution[3][3] == 1
        
        TestSudokuMIPSolverSolve.validate_4x4_solution(solution)
    
    def test_solve_unsolvable_board(self):
        """Test solving an unsolvable sudoku puzzle."""
        # Create a 4x4 board with conflicting values
        board = [
            [1, 1, None, None],  # Conflicting 1's in first row
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, None]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        result = solver.solve()
        
        # Should not be solvable
        assert result is False
        assert solver.current_solution is None
    
    def test_solve_complete_board(self):
        """Test solving an already complete valid board."""
        # Already solved 4x4 sudoku
        board = [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [2, 1, 4, 3],
            [4, 3, 2, 1]
        ]
        solver = SudokuMIPSolver(board, 2, 2)
        result = solver.solve()
        assert result is True
        assert solver.current_solution is not None
        assert solver.current_solution == board

        TestSudokuMIPSolverSolve.validate_4x4_solution(solver.current_solution)
    
    def test_solve_empty_board(self):
        """Test solving a completely empty board (many solutions)."""
        # Empty 4x4 board
        board = [[None for _ in range(4)] for _ in range(4)]
        
        solver = SudokuMIPSolver(board, 2, 2)
        result = solver.solve()
        assert result is True
        assert solver.current_solution is not None
        
        TestSudokuMIPSolverSolve.validate_4x4_solution(solver.current_solution)
    
    def test_find_all_solutions_unique(self):
        """Test finding all solutions for a board with a unique solution."""
        # This board has enough clues to have a unique solution
        board = [
            [1, None, 3, None],
            [3, None, None, 2],
            [None, 1, None, 3],
            [None, None, 2, None]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        solutions = solver.find_all_solutions()
        
        assert len(solutions) == 1
        
        TestSudokuMIPSolverSolve.validate_4x4_solution(solutions[0])
    
    def test_find_all_solutions_multiple(self):
        """Test finding all solutions for a board with multiple solutions."""
        # This board has fewer clues and multiple solutions
        board = [
            [1, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, 2]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        # Limit to 5 to avoid long runtime (has more than 5 solutions)
        sol_limit = 5
        solutions = solver.find_all_solutions(max_solutions=sol_limit)  
        
        # Should have multiple solutions
        assert len(solutions) == sol_limit
        
        # Verify all solutions follow sudoku rules and preserve initial values
        for solution in solutions:
            assert solution[0][0] == 1
            assert solution[3][3] == 2
            
            TestSudokuMIPSolverSolve.validate_4x4_solution(solution)

            
        # Verify all solutions are different
        solution_strs = [''.join(''.join(str(cell) for cell in row) for row in solution) 
                        for solution in solutions]
        assert len(set(solution_strs)) == sol_limit

    def test_cut_current_solution(self):
        """Test that cut_current_solution excludes the current solution."""
        # Simple 4x4 board with a unique solution
        board = [
            [1, None, 3, None],
            [None, None, None, 2],
            [None, 1, None, None],
            [None, None, 2, None]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        
        # Solve first time
        solver.solve()
        first_solution = [row[:] for row in solver.current_solution]  # Deep copy
        
        # Add constraint to exclude this solution
        solver.cut_current_solution()
        
        # Solve again
        solver.solve()
        
        second_solution = solver.current_solution
        assert second_solution != first_solution
            
        # Verify constraint was added
        assert len(solver.cut_constraints) == 1
        constraint_name = solver.cut_constraints[0][0]
        assert constraint_name == "cut_1"
        assert constraint_name in solver.model.constraints
    
    def test_cut_current_solution_no_solution(self):
        """Test that cut_current_solution raises an error when no solution exists."""
        board = [[None for _ in range(4)] for _ in range(4)]
        
        solver = SudokuMIPSolver(board, 2, 2)
        # Don't solve first, so there's no current_solution
        
        with pytest.raises(ValueError, match="No current solution to cut."):
            solver.cut_current_solution()
    
    def test_reset_model(self):
        """Test that reset_model removes solution cuts and restores original constraints."""
        # Board with multiple solutions
        board = [
            [1, None, None, None],
            [None, None, None, None],
            [None, None, None, None],
            [None, None, None, 2]
        ]
        
        solver = SudokuMIPSolver(board, 2, 2)
        
        # Find first solution
        solver.solve()
        original_solution = [row[:] for row in solver.current_solution]
        
        # Add cuts to exclude first solution
        solver.cut_current_solution()
        
        # Check constraint was added
        assert len(solver.cut_constraints) == 1
        assert any(name.startswith("cut_") for name in solver.model.constraints)
        
        # Find second solution (should be different)
        solver.solve()
        second_solution = [row[:] for row in solver.current_solution]
        assert original_solution != second_solution
        
        # Reset model
        solver.reset_model()
        
        # Verify reset worked
        assert solver.cut_constraints == []
        assert solver.current_solution is None
        assert not any(name.startswith("cut_") for name in solver.model.constraints)
        
        # Solve again - should get original solution back since cuts were removed
        solver.solve()
        assert solver.current_solution == original_solution

    def test_solve_standard_9x9(self):
        """Test solving a standard 9x9 sudoku puzzle."""
        # Using a 9x9 from test_from_string_standard_9x9
        sudoku_string = "700006200080001007046070300060090000050040020000010040009020570500100080008900003"
        solver = SudokuMIPSolver.from_string(sudoku_string)
        
        result = solver.solve()
        
        assert result is True
        assert solver.current_solution is not None
        
        # Verify initial values are preserved
        assert solver.current_solution[0][0] == 7
        assert solver.current_solution[0][5] == 6
        assert solver.current_solution[8][8] == 3
        
        # Verify solution follows sudoku rules
        for r in range(9):
            row_values = [solver.current_solution[r][c] for c in range(9)]
            assert sorted(row_values) == list(range(1, 10))
            
        for c in range(9):
            col_values = [solver.current_solution[r][c] for r in range(9)]
            assert sorted(col_values) == list(range(1, 10))
            
        # Check box constraints
        for box_r in range(3):
            for box_c in range(3):
                box_values = []
                for r in range(3):
                    for c in range(3):
                        box_values.append(solver.current_solution[box_r*3 + r][box_c*3 + c])
                assert sorted(box_values) == list(range(1, 10))

class TestSudokuMIPSolverRandomPuzzle:
    """Test cases for SudokuMIPSolver.generate_random_puzzle method."""

    def test_basic_puzzle_generation(self):
        """Test that a basic random puzzle can be generated successfully."""
        solver, difficulty = SudokuMIPSolver.generate_random_puzzle()
        
        # Check that we got a valid solver instance
        assert isinstance(solver, SudokuMIPSolver)
        assert solver.size == 9
        assert solver.sub_grid_width == 3
        assert solver.sub_grid_height == 3
        
        # Check that difficulty is within expected range
        assert 0.0 <= difficulty <= 1.0
        
        # Check board has some values filled in
        filled_cells = sum(1 for r in range(9) for c in range(9) if solver.board[r][c] is not None)
        assert filled_cells > 0
        
        # Verify the puzzle has a solution
        assert solver.solve()
    
    def test_random_seed_control(self):
        """Test that providing the same random seed produces the same puzzle."""
        # Generate two puzzles with the same seed
        solver1, diff1 = SudokuMIPSolver.generate_random_puzzle(random_seed=42)
        solver2, diff2 = SudokuMIPSolver.generate_random_puzzle(random_seed=42)
        
        # Generate a puzzle with a different seed
        solver3, _ = SudokuMIPSolver.generate_random_puzzle(random_seed=24)
        
        # The first two should be identical
        assert solver1.board == solver2.board
        assert diff1 == diff2
        
        # The third should be different
        assert solver1.board != solver3.board
    
    def test_difficulty_levels(self):
        """Test that different difficulty levels produce appropriately different puzzles."""
        # Generate easy puzzle (more filled cells)
        solver_easy, diff_easy = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=0.2, unique_solution=False, random_seed=42
        )
        
        # Generate hard puzzle (fewer filled cells)
        solver_hard, diff_hard = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=0.8, unique_solution=False, random_seed=42
        )
        
        filled_easy = sum(1 for r in range(9) for c in range(9) 
                          if solver_easy.board[r][c] is not None)
        filled_hard = sum(1 for r in range(9) for c in range(9) 
                          if solver_hard.board[r][c] is not None)
        
        # Hard should have fewer filled cells than easy
        assert filled_hard < filled_easy
        # Difficulty values should reflect the difference
        assert diff_hard > diff_easy
    
    def test_unique_solution(self):
        """Test that puzzles with unique_solution=True have only one solution."""
        # Generate puzzle with unique solution requirement
        solver, _ = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=0.5, unique_solution=True, max_attempts=10
        )
        
        # Test it has exactly one solution
        solutions = solver.find_all_solutions(max_solutions=2)
        assert len(solutions) == 1
    
    def test_non_unique_solution(self):
        """Test that puzzles with unique_solution=False may have multiple solutions."""
        # Note: This doesn't guarantee multiple solutions, but allows for them
        # random_seed = 1 with target_difficulty=0.95 gives a puzzle with multiple solutions
        solver, _ = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=0.95, unique_solution=False, random_seed=1
        )
        
        # Get solutions (up to 3)
        solutions = solver.find_all_solutions(max_solutions=3)
        
        # Check that it has multiple solutions
        assert len(solutions) > 1
    
    def test_invalid_difficulty(self):
        """Test that invalid difficulty values raise ValueError."""
        # Test negative difficulty
        with pytest.raises(ValueError, match="Difficulty must be between 0.0 and 1.0"):
            SudokuMIPSolver.generate_random_puzzle(target_difficulty=-0.1)
          # Test difficulty > 1.0
        with pytest.raises(ValueError, match="Difficulty must be between 0.0 and 1.0"):
            SudokuMIPSolver.generate_random_puzzle(target_difficulty=1.1)
    
    def test_different_board_sizes(self):
        """Test generating puzzles with different board sizes."""
        # 6x6 puzzle (2x3 sub-grids)
        solver_6x6, _ = SudokuMIPSolver.generate_random_puzzle(
            sub_grid_width=2, sub_grid_height=3
        )
        assert solver_6x6.size == 6
        assert solver_6x6.sub_grid_width == 2
        assert solver_6x6.sub_grid_height == 3
        
        # 12x12 puzzle (3x4 sub-grids)
        solver_12x12, _ = SudokuMIPSolver.generate_random_puzzle(
            sub_grid_width=3, sub_grid_height=4
        )
        assert solver_12x12.size == 12
        assert solver_12x12.sub_grid_width == 3
        assert solver_12x12.sub_grid_height == 4
        
        # Verify these are valid solvable puzzles
        assert solver_6x6.solve()
        assert solver_12x12.solve()
    
    def test_actual_vs_target_difficulty(self):
        """Test the relationship between target difficulty and actual achieved difficulty."""
        # With unique_solution=True, the actual difficulty may differ from the target
        target = 0.7
        solver, actual = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=target, unique_solution=True
        )
        
        # The actual difficulty should be a float between 0 and 1
        assert isinstance(actual, float)
        assert 0.0 <= actual <= 1.0
        assert pytest.approx(actual, rel=0.1) == target
    
    def test_max_attempts(self):
        """Test that max_attempts parameter limits generation attempts."""
        # Set a very difficult target that might be impossible to achieve with uniqueness
        # and limit attempts to just 1
        solver, actual = SudokuMIPSolver.generate_random_puzzle(
            target_difficulty=0.99, unique_solution=True, max_attempts=1
        )
        
        # Should still return a valid puzzle even if it couldn't meet the difficulty target
        assert isinstance(solver, SudokuMIPSolver)
        assert solver.solve()