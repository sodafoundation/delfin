from dolphin import utils


def test_set_bit():
    assert 0b10000000 == utils.set_bit(0, 7, 1)
    assert 0b01111111 == utils.set_bit(0b11111111, 7, 0)


def test_set_bits():
    assert 0b1011101 == utils.set_bits(0b1000001, 2, 4, 1)
    assert 0b1000001 == utils.set_bits(0b1011101, 2, 4, 0)
    assert 0b1111 == utils.set_bits(0, 0, 3, 1)
    assert 0 == utils.set_bits(0b1111, 0, 3, 0)
