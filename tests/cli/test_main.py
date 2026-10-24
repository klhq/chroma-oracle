"""Tests for the main CLI."""

from unittest import TestCase

from click.testing import CliRunner

from chroma_oracle.cli.main import cli


class TestCli(TestCase):
    """Unit test cases for the chroma_oracle cli."""

    def test_cli_no_arguments(self):
        """Invoke with no arguments and assert an error is raised."""
        runner = CliRunner()
        result = runner.invoke(cli, ["solve"])

        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Missing argument 'PUZZLE'." in result.output,
            "Required arguments must be present to run cli",
        )

    def test_cli_help(self):
        """Invoke with the help flag and assert that help test is printed."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        # Global help should NOT show subcommand-specific options anymore
        self.assertFalse("-a, --algorithm" in result.output, "Global options removed")
        self.assertTrue("--help" in result.output, "Help text should be printed")
        self.assertTrue("solve" in result.output, "Subcommand solve should be listed")
        self.assertTrue(
            "strategy" in result.output, "Subcommand strategy should be listed"
        )

    def test_solve_help(self):
        """Invoke solve subcommand with help to see options."""
        runner = CliRunner()
        result = runner.invoke(cli, ["solve", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("-a, --algorithm" in result.output, "Options should be shown")
        self.assertTrue("-v, --validate" in result.output, "Options should be shown")
        self.assertTrue("--verbose" in result.output, "Options should be shown")

    def test_cli_verbose(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["solve", "--verbose", "./levels/debug.json"])
        self.assertEqual(result.exit_code, 0)

    def test_cli_bad_puzzle(self):
        """Invoke with a bad puzzle that cannot be solved."""
        runner = CliRunner()
        result = runner.invoke(cli, ["solve", "./levels/bad.json"])

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Cannot be solved :(" in result.output,
            "This puzzle cannot be solved",
        )

    def test_cli_bad_puzzle_fail_validate(self):
        """Invoke with a bad puzzle that cannot be solved."""
        runner = CliRunner()
        result = runner.invoke(cli, ["solve", "--validate", "./levels/bad.json"])

        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Error: Invalid PUZZLE: Invalid colour count" in result.output,
            "This puzzle fails validation",
        )

    def test_cli_bfs_algorithm(self):
        """Invoke with the BFS algorithm and a known puzzle.

        This shoud take 10 moves to solve and results in a known output that
        can be tested for.
        """
        runner = CliRunner()
        result = runner.invoke(
            cli, ["solve", "--algorithm=bfs", "./levels/simple_shows_differences.json"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Searching using Breadth-First Search" in result.output,
            "Should show BFS was used for the search",
        )
        self.assertTrue(
            "solved in 10 moves" in result.output,
            "BFS takes 10 moves to solve this puzzle",
        )
        self.assertTrue(
            "1. Container 0 -> 3" in result.output
            and "10. Container 2 -> 4" in result.output,
            "BFS numbered moves output for this puzzle",
        )

    def test_cli_dfs_algorithm(self):
        """Invoke with the DFS algorithm and a known puzzle.

        This shoud take 10 moves to solve and results in a known output that
        can be tested for.
        """
        runner = CliRunner()
        result = runner.invoke(
            cli, ["solve", "--algorithm=dfs", "./levels/simple_shows_differences.json"]
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Searching using Depth-First Search" in result.output,
            "Should show DFS was used for the search",
        )
        self.assertTrue(
            "solved in 13 moves" in result.output,
            "DFS takes 13 moves to solve this puzzle",
        )
        # Legacy raw tuple output removed; verify numbered moves printed instead
        self.assertTrue(
            "1. Container 0 -> 3" in result.output
            and "13. Container 2 -> 4" in result.output,
            "DFS numbered moves output for this puzzle",
        )

    def test_entrypoint(self):
        """Test directly running the module with the help argument.

        This test just validates the return code.
        """
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "chroma_oracle", "--help"],
            encoding="ascii",
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertFalse("-a, --algorithm" in result.stdout, "Global options removed")
        self.assertTrue("--help" in result.stdout, "Help text should be printed")

    def test_strategy_too_many_candidates(self):
        """Test strategy CLI command fails gracefully when candidate cap exceeded."""
        import json
        import tempfile

        runner = CliRunner()
        puzzle_grid = [
            ["RED", "RED", "RED", "?"],
            ["BLUE", "BLUE", "BLUE", "?"],
            ["GREEN", "GREEN", "GREEN", "?"],
            ["YELLOW", "YELLOW", "YELLOW", "?"],
            ["ORANGE", "ORANGE", "ORANGE", "?"],
            ["PURPLE", "PURPLE", "PURPLE", "?"],
            [],
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            json.dump(puzzle_grid, f)
            f.flush()
            result = runner.invoke(cli, ["strategy", f.name])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("720 candidates", result.output)
            self.assertIn("cap: 200", result.output)

    def test_cli_solve_oversized_tube(self):
        """CLI solve command rejects tubes longer than 4 with readable error."""
        import json
        import tempfile

        runner = CliRunner()
        oversized_puzzle = [
            ["RED", "RED", "BLUE", "BLUE", "GREEN"],
            ["GREEN", "GREEN", "GREEN"],
            [],
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            json.dump(oversized_puzzle, f)
            f.flush()
            result = runner.invoke(cli, ["solve", f.name])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error: Invalid PUZZLE:", result.output)
            self.assertIn("Tube 0", result.output)
            self.assertIn("5 items", result.output)
            self.assertNotIn("Traceback", result.output)

    def test_cli_strategy_oversized_tube(self):
        """CLI strategy command rejects tubes longer than 4 with readable error."""
        import json
        import tempfile

        runner = CliRunner()
        oversized_puzzle = [
            ["RED", "RED", "BLUE", "BLUE", "GREEN"],
            ["GREEN", "GREEN", "GREEN"],
            [],
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            json.dump(oversized_puzzle, f)
            f.flush()
            result = runner.invoke(cli, ["strategy", f.name])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error: Invalid PUZZLE:", result.output)
            self.assertIn("Tube 0", result.output)
            self.assertIn("5 items", result.output)
            self.assertNotIn("Traceback", result.output)

    def test_cli_solve_tube_of_exactly_four_accepted(self):
        """CLI solve accepts tubes of exactly 4 items."""
        import json
        import tempfile

        runner = CliRunner()
        valid_puzzle = [
            ["RED", "RED", "RED", "RED"],
            [],
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            json.dump(valid_puzzle, f)
            f.flush()
            result = runner.invoke(cli, ["solve", f.name])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("solved in 0 moves", result.output)
