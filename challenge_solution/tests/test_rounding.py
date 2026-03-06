from src.wns_challenge.service import round_up_to_step


def test_rounding_examples() -> None:
    assert round_up_to_step(800, 250) == 1000
    assert round_up_to_step(250, 250) == 250
    assert round_up_to_step(1, 250) == 250


def test_rounding_zero() -> None:
    assert round_up_to_step(0, 250) == 0
