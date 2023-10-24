"""Tests for encoding and decoding"""
import migen as nm
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
    jal = nm.Constant(encoding.JType.encode(offset, 5), shape=32)
    extended_offset = int(f"{offset:021b}"[0]*11 + f"{offset:021b}", 2)
    assert (extended_offset & 0x1ffffe) == offset

    def testbench():
        assert (yield encoding.JType(jal).immediate()) == extended_offset

    comb_sim(m, testbench)


@pytest.mark.parametrize(
        "imm",
        [
            0b11110000111,
            0b01010101010,
            0b11111111111,
            0b00010010010,
        ])
def test_itype_same_immediate_out_as_in(comb_sim, imm):
    m = nm.Module()
    addi = nm.Constant(
            encoding.IType.encode(
                imm,
                1,
                encoding.IntRegImmFunct.ADDI,
                2,
                encoding.Opcode.OP_IMM),
            shape=32)
    extended_imm = int(f"{imm:012b}"[0]*20 + f"{imm:012b}", 2)
    assert (extended_imm & 0x7ff) == imm

    def testbench():
        assert (yield encoding.IType(addi).immediate()) == extended_imm

    comb_sim(m, testbench)
