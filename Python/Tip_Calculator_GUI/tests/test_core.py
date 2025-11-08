from decimal import Decimal
from tipcalc.core import compute_tip, _round_to_step
import pytest

def dec(x):
    return Decimal(str(x))

def test_basic_compute():
    """Test basic tip calculation"""
    res = compute_tip(100, 10, people=1)
    assert res.tip_amount == dec("10")
    assert res.total == dec("110")
    assert res.per_person == dec("110")

def test_split_and_round_nearest():
    """Test splitting bill and rounding to nearest"""
    res = compute_tip(
        123.45, 18, people=3, round_to=0.05, round_target="per_person", round_mode="nearest"
    )
    assert res.per_person == dec("48.55")
    assert res.total == dec("145.65")

def test_round_up():
    """Test rounding up"""
    res = compute_tip(
        100, 15, people=3, round_to=1.00, round_target="total", round_mode="up"
    )
    assert res.total == dec("116.00")  # 115 rounded up to 116

def test_round_down():
    """Test rounding down"""
    res = compute_tip(
        100, 15, people=3, round_to=1.00, round_target="total", round_mode="down"
    )
    assert res.total == dec("115.00")  # 115 remains 115 when rounding down

def test_validation():
    """Test input validation"""
    with pytest.raises(ValueError):
        compute_tip(-1, 10)
    with pytest.raises(ValueError):
        compute_tip(100, -5)
    with pytest.raises(ValueError):
        compute_tip(100, 10, people=0)

def test_round_to_step():
    """Test the _round_to_step function directly"""
    # Test nearest rounding
    assert _round_to_step(Decimal('10.73'), Decimal('0.05'), 'nearest') == Decimal('10.75')
    assert _round_to_step(Decimal('10.72'), Decimal('0.05'), 'nearest') == Decimal('10.70')
    
    # Test rounding up
    assert _round_to_step(Decimal('10.71'), Decimal('0.05'), 'up') == Decimal('10.75')
    
    # Test rounding down
    assert _round_to_step(Decimal('10.79'), Decimal('0.05'), 'down') == Decimal('10.75')

def test_edge_cases():
    """Test edge cases"""
    # Zero tip
    res = compute_tip(100, 0, people=2)
    assert res.tip_amount == dec("0")
    assert res.total == dec("100")
    assert res.per_person == dec("50")
    
    # Large numbers
    res = compute_tip(10000, 20, people=10)
    assert res.tip_amount == dec("2000")
    assert res.total == dec("12000")
    assert res.per_person == dec("1200")