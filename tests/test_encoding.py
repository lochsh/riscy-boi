import nmigen.sim
import nmigen as nm
import pytest

from riscy_boi import encoding


@pytest.mark.parametrize(
        "offset",
        [   # note LSB is always zero
            0b000001111000011110000,
            0b100000000000000000000,
            0b111110000111100001110,
            0b001010101010101010100,
            0b111111111111111111110,
            0b110010100010001001100,
            0b100110100010011001110,
        ])
def test_jtype_same_offset_out_as_in(comb_sim, offset):
    m = nm.Module()
    jal = encoding.JType.encode(offset, 5)
    extended_offset = int(f"{offset:021b}"[0]*11 + f"{offset:021b}", 2)
    assert (extended_offset & 0x1ffffe) == offset

    def testbench():
        assert (yield encoding.JType(jal).immediate()) == extended_offset

    comb_sim(m, testbench)
