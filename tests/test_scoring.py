"""Tests for scoring functions."""

import pytest
from src.main import score_points, score_class, sign


class TestSign:
    """Test the sign function."""
    
    def test_sign_positive(self):
        assert sign(5) == 1
        assert sign(1) == 1
        assert sign(100) == 1
    
    def test_sign_zero(self):
        assert sign(0) == 0
    
    def test_sign_negative(self):
        assert sign(-5) == -1
        assert sign(-1) == -1
        assert sign(-100) == -1


class TestScorePoints:
    """Test the score_points function."""
    
    def test_exact_match(self):
        """Exact match should return 3 points."""
        assert score_points((2, 1), (2, 1)) == 3
        assert score_points((0, 0), (0, 0)) == 3
        assert score_points((5, 3), (5, 3)) == 3
    
    def test_correct_goal_difference(self):
        """Correct goal difference should return 2 points."""
        # Predicted 2-1 (GD=1), actual 3-2 (GD=1)
        assert score_points((2, 1), (3, 2)) == 2
        # Predicted 0-2 (GD=-2), actual 1-3 (GD=-2)
        assert score_points((0, 2), (1, 3)) == 2
        # Predicted 1-0 (GD=1), actual 3-2 (GD=1)
        assert score_points((1, 0), (3, 2)) == 2
    
    def test_correct_winner(self):
        """Correct winner (same sign of GD) should return 1 point."""
        # Predicted home win (2-1, GD=1), actual home win (3-0, GD=3)
        assert score_points((2, 1), (3, 0)) == 1
        # Predicted away win (1-2, GD=-1), actual away win (0-3, GD=-3)
        assert score_points((1, 2), (0, 3)) == 1
        # Both are draws (GD=0)
        assert score_points((1, 1), (2, 2)) == 2  # GD match
    
    def test_no_points(self):
        """Wrong prediction should return 0 points."""
        # Predicted home win (2-1), actual away win (1-2)
        assert score_points((2, 1), (1, 2)) == 0
        # Predicted draw (1-1), actual home win (2-0)
        assert score_points((1, 1), (2, 0)) == 0
        # Large difference
        assert score_points((0, 0), (5, 3)) == 0


class TestScoreClass:
    """Test the score_class function."""
    
    def test_score_class_exact_match(self):
        """Exact match should return 'points3'."""
        assert score_class((2, 1), (2, 1)) == 'points3'
        assert score_class((0, 0), (0, 0)) == 'points3'
    
    def test_score_class_correct_difference(self):
        """Correct goal difference should return 'points2'."""
        assert score_class((2, 1), (3, 2)) == 'points2'
    
    def test_score_class_correct_winner(self):
        """Correct winner should return 'points1'."""
        assert score_class((2, 1), (3, 0)) == 'points1'
    
    def test_score_class_no_points(self):
        """Wrong prediction should return 'points0'."""
        assert score_class((2, 1), (1, 2)) == 'points0'
    
    def test_score_class_with_none_predicted(self):
        """None in predicted score should return empty string."""
        assert score_class((None, 1), (2, 1)) == ''
        assert score_class((2, None), (2, 1)) == ''
    
    def test_score_class_with_none_actual(self):
        """None in actual score should return empty string."""
        assert score_class((2, 1), (None, 1)) == ''
        assert score_class((2, 1), (2, None)) == ''
    
    def test_score_class_with_empty_string_predicted(self):
        """Empty string in predicted score should return empty string."""
        assert score_class(("", 1), (2, 1)) == ''
        assert score_class((2, ""), (2, 1)) == ''
    
    def test_score_class_with_empty_string_actual(self):
        """Empty string in actual score should return empty string."""
        assert score_class((2, 1), ("", 1)) == ''
        assert score_class((2, 1), (2, "")) == ''
    
    def test_score_class_with_string_numbers(self):
        """String numbers should be converted to int."""
        assert score_class(("2", "1"), ("2", "1")) == 'points3'
        assert score_class(("2", "1"), ("3", "2")) == 'points2'
