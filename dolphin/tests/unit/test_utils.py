from dolphin import utils


def test_set_bit():
    assert 128 == utils.set_bit(0, 7, 1)
    assert 127 == utils.set_bit(255, 7, 0)
