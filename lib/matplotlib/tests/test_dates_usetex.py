"""
Test for the datetime axis usetex formatting fix.
Tests that _wrap_in_tex produces consistent LaTeX formatting.
"""

import re
import pytest
from matplotlib.dates import _wrap_in_tex


class TestWrapInTex:
    """Test the _wrap_in_tex function for consistent LaTeX formatting."""
    
    def test_basic_formatting(self):
        """Test basic datetime formats"""
        # Test time formats
        assert _wrap_in_tex("01 00:00") == r"$\mathdefault{01\;00{:}00}$"
        assert _wrap_in_tex("12:30:45") == r"$\mathdefault{12{:}30{:}45}$"
        
        # Test date formats
        assert _wrap_in_tex("2020-01-01") == r"$\mathdefault{2020{-}01{-}01}$"
        
    def test_letter_handling(self):
        """Test that letters are handled consistently (main fix)"""
        # These were problematic in the original implementation
        assert _wrap_in_tex("Jan 01") == r"$\mathdefault{Jan\;01}$"
        assert _wrap_in_tex("Feb 15") == r"$\mathdefault{Feb\;15}$"
        assert _wrap_in_tex("Mar 30") == r"$\mathdefault{Mar\;30}$"
        
    def test_consistency(self):
        """Test that all outputs follow the same pattern"""
        test_cases = [
            "01 00:00", "01 00:05", "01 00:10",
            "Jan 01", "Feb 15", "Mar 30", 
            "2020-01-01", "2021-12-31",
            "00:00", "12:30:45"
        ]
        
        pattern = r'^\$\\mathdefault\{.*\}\$$'
        
        for test_case in test_cases:
            result = _wrap_in_tex(test_case)
            assert re.match(pattern, result), f"'{test_case}' -> '{result}' doesn't match pattern"
            
    def test_special_characters(self):
        """Test proper escaping of special characters"""
        # Spaces should become \;
        result = _wrap_in_tex("a b")
        assert r"\;" in result
        
        # Colons should be braced
        result = _wrap_in_tex("a:b")
        assert "{:}" in result
        
        # Dashes should be braced
        result = _wrap_in_tex("a-b")
        assert "{-}" in result
        
    def test_edge_cases(self):
        """Test edge cases"""
        # Empty string
        assert _wrap_in_tex("") == r"$\mathdefault{}$"
        
        # Single character
        assert _wrap_in_tex("a") == r"$\mathdefault{a}$"
        
        # Only numbers
        assert _wrap_in_tex("123") == r"$\mathdefault{123}$"
        
    def test_no_multiple_math_modes(self):
        """Test that result never has multiple math mode blocks"""
        test_cases = [
            "Jan 01", "Feb 15", "Mar 30",  # These were problematic
            "Apr 20", "May 25", "Jun 30",
            "text with spaces", "a:b:c", "x-y-z"
        ]
        
        for test_case in test_cases:
            result = _wrap_in_tex(test_case)
            # Count dollar signs - should be exactly 2 (opening and closing)
            dollar_count = result.count('$')
            assert dollar_count == 2, f"'{test_case}' -> '{result}' has {dollar_count} dollar signs, expected 2"