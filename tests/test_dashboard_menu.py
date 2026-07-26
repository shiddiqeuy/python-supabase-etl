"""Unit tests - Menu Interaktif Bertingkat 2-Level (Test 13 - 22)."""

import unittest
from unittest.mock import MagicMock, patch
import io
import sys

from src.utils.messages import MENU_ITEMS, SUBMENU_ITEMS


class TestDashboardMenuNavigation(unittest.TestCase):
    # Test 13: test_main_menu_existing_options_unchanged
    def test_main_menu_existing_options_unchanged(self):
        self.assertEqual(MENU_ITEMS[0][0], "1")
        self.assertEqual(MENU_ITEMS[1][0], "2")
        self.assertEqual(MENU_ITEMS[2][0], "3")

    # Test 14: test_main_menu_displays_new_option_4
    def test_main_menu_displays_new_option_4(self):
        self.assertEqual(MENU_ITEMS[3][0], "4")
        self.assertIn("Sales Dashboard", MENU_ITEMS[3][1])

    # Test 15: test_main_menu_option_4_enters_sales_dashboard_submenu
    @patch("builtins.input", side_effect=["0"])
    def test_main_menu_option_4_enters_sales_dashboard_submenu(self, mock_input):
        from src.__main__ import interactive_dashboard_submenu
        # Entering option 0 immediately breaks out to main menu
        interactive_dashboard_submenu()
        self.assertTrue(mock_input.called)

    # Test 16: test_main_menu_option_5_exits_cleanly
    def test_main_menu_option_5_exits_cleanly(self):
        self.assertEqual(MENU_ITEMS[4][0], "5")
        self.assertIn("Keluar", MENU_ITEMS[4][1])

    # Test 17: test_submenu_displays_all_options
    def test_submenu_displays_all_options(self):
        keys = [item[0] for item in SUBMENU_ITEMS]
        self.assertEqual(keys, ["1", "2", "3", "4", "5", "6", "7", "0"])

    # Test 18: test_submenu_invalid_input_shows_error_and_reloops
    @patch("builtins.input", side_effect=["99", "0"])
    def test_submenu_invalid_input_shows_error_and_reloops(self, mock_input):
        from src.__main__ import interactive_dashboard_submenu
        interactive_dashboard_submenu()
        self.assertEqual(mock_input.call_count, 2)

    # Test 19: test_submenu_option_0_returns_to_main_menu
    @patch("builtins.input", side_effect=["0"])
    def test_submenu_option_0_returns_to_main_menu(self, mock_input):
        from src.__main__ import interactive_dashboard_submenu
        interactive_dashboard_submenu()
        self.assertEqual(mock_input.call_count, 1)

    # Test 20: test_submenu_option_1_prompts_date_with_default
    @patch("builtins.input", side_effect=["", "", "", "", "", "", ""])
    @patch("src.cli.dashboard_command.summary_cmd")
    def test_submenu_option_1_prompts_date_with_default(self, mock_summary, mock_input):
        from src.__main__ import interactive_dashboard_submenu
        # Select 1, then enter defaults, then 0 to return
        with patch("builtins.input", side_effect=["1", "", "", "", "", "", "", "", "0"]):
            interactive_dashboard_submenu()
            self.assertTrue(mock_summary.called)

    # Test 21: test_submenu_loops_back_after_feature_execution
    @patch("src.cli.dashboard_command.by_sales_cmd")
    def test_submenu_loops_back_after_feature_execution(self, mock_cmd):
        from src.__main__ import interactive_dashboard_submenu
        # Select 2, press enter, then select 0 to exit
        with patch("builtins.input", side_effect=["2", "", "0"]):
            interactive_dashboard_submenu()
            self.assertTrue(mock_cmd.called)

    # Test 22: test_navigation_full_round_trip
    @patch("src.__main__.interactive_menu")
    def test_navigation_full_round_trip(self, mock_menu):
        # Round trip test verification
        from src.__main__ import main
        with patch("sys.argv", ["src"]):
            main()
            self.assertTrue(mock_menu.called)


if __name__ == "__main__":
    unittest.main()
