import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import argparse
import os

# Import from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sudoku_mip_solver import cli

# Helper to set command line arguments
def set_argv(args):
    """Helper function to set sys.argv for testing."""
    sys.argv = ['cli.py'] + args


class TestParseArguments:
    """Test cases for the parse_arguments function."""

    def test_defaults(self):
        """Test that default arguments are parsed correctly."""
        set_argv([])
        args = cli.parse_arguments()
        assert args.string is None
        assert args.file is None
        assert args.generate_only is False
        assert args.width == 3
        assert args.height is None
        assert args.difficulty == 0.75
        assert args.non_unique is False
        assert args.max_solutions == 1
        assert args.output is None
        assert args.verbose is False
        assert args.quiet is False

    def test_all_flags(self):
        """Test parsing of all command-line flags."""
        set_argv([
            '--string', '123',
            '--width', '2',
            '--height', '2',
            '--difficulty', '0.8',
            '--non-unique',
            '--max-solutions', '10',
            '--output', 'out.txt',
            '--verbose'
        ])
        args = cli.parse_arguments()
        assert args.string == '123'
        assert args.width == 2
        assert args.height == 2
        assert args.difficulty == 0.8
        assert args.non_unique is True
        assert args.max_solutions == 10
        assert args.output == 'out.txt'
        assert args.verbose is True
        assert args.quiet is False

    def test_mutually_exclusive_input(self):
        """Test that mutually exclusive input arguments raise an error."""
        set_argv(['--string', '123', '--file', 'in.txt'])
        with pytest.raises(SystemExit):
            cli.parse_arguments()

    def test_mutually_exclusive_verbosity(self):
        """Test that mutually exclusive verbosity flags raise an error."""
        set_argv(['--verbose', '--quiet'])
        with pytest.raises(SystemExit):
            cli.parse_arguments()

    def test_version_flag(self):
        """Test that the --version flag exits with version information."""
        from sudoku_mip_solver import __version__
        
        with pytest.raises(SystemExit) as excinfo:
            set_argv(['--version'])
            cli.parse_arguments()
        
        # The exit code should be 0 (success)
        assert excinfo.value.code == 0

    def test_version_output(self, capsys, monkeypatch):
        """Test that --version outputs the correct version."""
        from sudoku_mip_solver import __version__
        
        # Mock sys.exit to prevent actual exit
        monkeypatch.setattr(sys, 'exit', lambda x: None)
        
        set_argv(['--version'])
        try:
            cli.parse_arguments()
        except SystemExit:
            pass
        
        # Check that version was printed to stdout
        captured = capsys.readouterr()
        assert f"cli.py {__version__}" in captured.out


class TestValidateArguments:
    """Test cases for the validate_arguments function."""

    def test_valid_args(self):
        """Test that valid arguments pass validation."""
        args = argparse.Namespace(width=3, height=3, difficulty=0.5, max_solutions=1)
        try:
            cli.validate_arguments(args)
        except ValueError:
            pytest.fail("validate_arguments raised ValueError unexpectedly!")

    def test_invalid_width(self):
        """Test that a non-positive width raises a ValueError."""
        args = argparse.Namespace(width=0, height=3, difficulty=0.5, max_solutions=1)
        with pytest.raises(ValueError, match="--width must be a positive integer"):
            cli.validate_arguments(args)

    def test_invalid_height(self):
        """Test that a non-positive height raises a ValueError."""
        args = argparse.Namespace(width=3, height=0, difficulty=0.5, max_solutions=1)
        with pytest.raises(ValueError, match="--height must be a positive integer"):
            cli.validate_arguments(args)

    def test_invalid_difficulty(self):
        """Test that an out-of-range difficulty raises a ValueError."""
        args = argparse.Namespace(width=3, height=3, difficulty=1.1, max_solutions=1)
        with pytest.raises(ValueError, match="--difficulty must be between 0.0 and 1.0"):
            cli.validate_arguments(args)

    def test_invalid_max_solutions(self):
        """Test that an invalid max_solutions value raises a ValueError."""
        args = argparse.Namespace(width=3, height=3, difficulty=0.5, max_solutions=0)
        with pytest.raises(ValueError, match="--max-solutions must be a positive integer or -1"):
            cli.validate_arguments(args)


class TestFileOperations:
    """Test cases for file reading and writing."""

    @patch("builtins.open", new_callable=mock_open, read_data="1234")
    def test_read_puzzle_from_file(self, mock_file):
        """Test reading a puzzle from a file."""
        content = cli.read_puzzle_from_file("anypath.txt")
        mock_file.assert_called_with("anypath.txt", 'r')
        assert content == "1234"

    @patch("builtins.open", side_effect=IOError("File not found"))
    def test_read_puzzle_from_file_error(self, mock_file):
        """Test that an IOError is raised when the file cannot be read."""
        with pytest.raises(IOError, match="Error reading file 'bad.txt': File not found"):
            cli.read_puzzle_from_file("bad.txt")

    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_file(self, mock_file):
        """Test saving content to a file."""
        cli.save_to_file("output.txt", "solution_string", "solution")
        mock_file.assert_called_with("output.txt", 'w')
        mock_file().write.assert_called_once_with("solution_string")


class TestGetSolver:
    """Test cases for the get_solver function."""

    @patch('sudoku_mip_solver.SudokuMIPSolver.from_string')
    def test_get_solver_from_string(self, mock_from_string, capsys):
        """Test creating a solver from a string argument."""
        args = argparse.Namespace(string="123", file=None, width=3, height=3, verbose=False, quiet=False)
        cli.get_solver(args)
        mock_from_string.assert_called_with("123", 3, 3)
        captured = capsys.readouterr()
        assert "Input puzzle:" in captured.out

    @patch('sudoku_mip_solver.cli.read_puzzle_from_file', return_value="456")
    @patch('sudoku_mip_solver.SudokuMIPSolver.from_string')
    def test_get_solver_from_file(self, mock_from_string, mock_read_file, capsys):
        """Test creating a solver from a file argument."""
        args = argparse.Namespace(string=None, file="puzzle.txt", width=3, height=3, verbose=False, quiet=False)
        cli.get_solver(args)
        mock_read_file.assert_called_with("puzzle.txt")
        mock_from_string.assert_called_with("456", 3, 3)
        captured = capsys.readouterr()
        assert "Puzzle from file:" in captured.out
    
    @patch('sudoku_mip_solver.cli.generate_random_puzzle')
    def test_get_solver_generate_random(self, mock_generate):
        """Test creating a solver by generating a random puzzle."""
        mock_solver = MagicMock()
        mock_generate.return_value = (mock_solver, 0.5)
        args = argparse.Namespace(string=None, file=None, width=3, height=None)
        solver = cli.get_solver(args)
        mock_generate.assert_called_with(args)
        assert solver == mock_solver


class TestSolveAndReport:
    """Test cases for the solve_and_report function."""

    def test_solve_and_report_single_solution(self, capsys):
        """Test reporting a single solution."""
        mock_solver = MagicMock()
        mock_solver.solve.return_value = True
        mock_solver.current_solution = [[1]]
        args = argparse.Namespace(max_solutions=1, verbose=False, quiet=False, output=None)
        
        with patch('time.time', side_effect=[0, 1]): # Mock timing
            cli.solve_and_report(mock_solver, args)
        
        mock_solver.solve.assert_called_once()
        mock_solver.pretty_print.assert_called_with([[1]])
        captured = capsys.readouterr()
        assert "No solution found!" not in captured.err

    def test_solve_and_report_no_solution(self, capsys):
        """Test reporting when no solution is found."""
        mock_solver = MagicMock()
        mock_solver.solve.return_value = False
        args = argparse.Namespace(max_solutions=1, verbose=False, quiet=False, output=None)

        with patch('time.time', side_effect=[0, 1]):
            cli.solve_and_report(mock_solver, args)

        captured = capsys.readouterr()
        assert "No solution found!" in captured.err

    @patch('sudoku_mip_solver.cli.save_solutions')
    def test_solve_and_report_with_output(self, mock_save):
        """Test that solutions are saved to a file when --output is provided."""
        mock_solver = MagicMock()
        mock_solver.solve.return_value = True
        mock_solver.current_solution = [[1]]
        args = argparse.Namespace(max_solutions=1, verbose=False, quiet=False, output="sol.txt")

        with patch('time.time', side_effect=[0, 1]):
            cli.solve_and_report(mock_solver, args)
        
        mock_save.assert_called_with(mock_solver, [[[1]]], "sol.txt")


class TestMainFunction:
    """Integration-style tests for the main function."""

    @patch('sudoku_mip_solver.cli.parse_arguments')
    @patch('sudoku_mip_solver.cli.validate_arguments')
    @patch('sudoku_mip_solver.cli.get_solver')
    @patch('sudoku_mip_solver.cli.solve_and_report')
    def test_main_solve_flow(self, mock_solve_report, mock_get_solver, mock_validate, mock_parse):
        """Test the main execution path for solving a puzzle."""
        args = argparse.Namespace(generate_only=False, verbose=False)
        mock_parse.return_value = args
        mock_solver = MagicMock()
        mock_get_solver.return_value = mock_solver

        cli.main()

        mock_validate.assert_called_with(args)
        mock_get_solver.assert_called_with(args)
        mock_solve_report.assert_called_with(mock_solver, args)

    @patch('sudoku_mip_solver.cli.parse_arguments')
    @patch('sudoku_mip_solver.cli.validate_arguments')
    @patch('sudoku_mip_solver.cli.main_generate_only')
    def test_main_generate_only_flow(self, mock_generate_only, mock_validate, mock_parse):
        """Test the main execution path for --generate-only."""
        args = argparse.Namespace(generate_only=True, verbose=False)
        mock_parse.return_value = args

        cli.main()

        mock_validate.assert_called_with(args)
        mock_generate_only.assert_called_with(args)

    @patch('sudoku_mip_solver.cli.parse_arguments')
    @patch('sudoku_mip_solver.cli.validate_arguments', side_effect=ValueError("Test error"))
    def test_main_validation_error(self, mock_validate, mock_parse, capsys):
        """Test that a validation error is caught and printed to stderr."""
        mock_parse.return_value = argparse.Namespace()
        with pytest.raises(SystemExit):
            cli.main()
        
        captured = capsys.readouterr()
        assert "Test error" in captured.err


class TestMainGenerateOnly:
    """Test cases for the main_generate_only function."""

    @patch('sudoku_mip_solver.cli.generate_random_puzzle')
    def test_main_generate_only(self, mock_generate, capsys):
        """Test the main_generate_only function."""
        mock_solver = MagicMock()
        mock_board = [[1, 2], [3, 4]]
        mock_solver.to_string.return_value = "1234"
        mock_generate.return_value = (mock_solver, mock_board)
        
        args = argparse.Namespace(quiet=False, output=None)
        cli.main_generate_only(args)
        
        mock_solver.to_string.assert_called_with(board=mock_board)
        captured = capsys.readouterr()
        assert "1234" in captured.out
    
    @patch('sudoku_mip_solver.cli.generate_random_puzzle')
    @patch('sudoku_mip_solver.cli.save_to_file')
    def test_main_generate_only_with_output(self, mock_save, mock_generate):
        """Test main_generate_only with output to file."""
        mock_solver = MagicMock()
        mock_board = [[1, 2], [3, 4]]
        mock_solver.to_string.return_value = "1234"
        mock_generate.return_value = (mock_solver, mock_board)
        
        args = argparse.Namespace(quiet=True, output="puzzle.txt")
        cli.main_generate_only(args)
        
        mock_save.assert_called_with("puzzle.txt", "1234", "generated puzzle")
    
    @patch('sudoku_mip_solver.cli.generate_random_puzzle')
    def test_main_generate_only_quiet(self, mock_generate):
        """Test main_generate_only with quiet option."""
        mock_solver = MagicMock()
        mock_board = [[1, 2], [3, 4]]
        mock_generate.return_value = (mock_solver, mock_board)
        
        args = argparse.Namespace(quiet=True, output=None)
        cli.main_generate_only(args)
        
        # Should not call to_string when quiet=True and no output
        mock_solver.to_string.assert_not_called()


class TestGenerateRandomPuzzle:
    """Test cases for the generate_random_puzzle function."""
    
    @patch('sudoku_mip_solver.SudokuMIPSolver.generate_random_puzzle')
    def test_generate_random_puzzle(self, mock_generate):
        """Test generating a random puzzle."""
        # Set up the mock
        mock_solver = MagicMock()
        mock_board = [[1, 2], [3, 4]]
        mock_generate.return_value = (mock_solver, 0.5)
        mock_solver.board = mock_board
        mock_solver.size = len(mock_board)
        
        # Test arguments
        args = argparse.Namespace(width=3, height=3, difficulty=0.5, non_unique=False, verbose=False, quiet=False)
        
        # Call the function
        solver, board = cli.generate_random_puzzle(args)
        
        # Assert the results
        assert solver == mock_solver
        assert board == mock_board
        
        # Verify the expected calls were made
        mock_generate.assert_called_once_with(
            sub_grid_width=3, 
            sub_grid_height=3, 
            target_difficulty=0.5, 
            unique_solution=True
        )
    
    @patch('sudoku_mip_solver.SudokuMIPSolver.generate_random_puzzle')
    def test_generate_random_puzzle_non_unique(self, mock_generate):
        """Test generating a random puzzle with non-unique option."""
        # Set up the mock
        mock_solver = MagicMock()
        mock_board = [[5, 6], [7, 8]]
        mock_generate.return_value = (mock_solver, 0.8)
        mock_solver.board = mock_board
        mock_solver.size = len(mock_board)
        
        # Test arguments with non_unique=True
        args = argparse.Namespace(width=2, height=2, difficulty=0.8, non_unique=True, verbose=False, quiet=False)
        
        # Call the function
        solver, board = cli.generate_random_puzzle(args)
        
        # Assert the results
        assert solver == mock_solver
        assert board == mock_board
        
        # Verify the expected calls were made
        mock_generate.assert_called_once_with(
            sub_grid_width=2, 
            sub_grid_height=2, 
            target_difficulty=0.8, 
            unique_solution=False
        )
    
    @patch('sudoku_mip_solver.SudokuMIPSolver.generate_random_puzzle')
    def test_generate_random_puzzle_default_height(self, mock_generate):
        """Test generating a random puzzle with default height (None)."""
        # Set up the mock
        mock_solver = MagicMock()
        mock_board = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        mock_generate.return_value = (mock_solver, 0.7)
        mock_solver.board = mock_board
        mock_solver.size = len(mock_board)
        
        # Test arguments with height=None (should default to width)
        args = argparse.Namespace(width=3, height=None, difficulty=0.7, non_unique=False, verbose=False, quiet=False)
        
        # Call the function
        solver, board = cli.generate_random_puzzle(args)
        
        # Assert the results
        assert solver == mock_solver
        assert board == mock_board
        
        # Verify the expected calls were made with the same value for width and height
        mock_generate.assert_called_once_with(
            sub_grid_width=3, 
            sub_grid_height=3, 
            target_difficulty=0.7, 
            unique_solution=True
        )