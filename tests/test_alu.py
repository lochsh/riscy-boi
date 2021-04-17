"""ALU tests"""
import nmigen.sim
import pytest

from riscy_boi import alu


@pytest.mark.parametrize(
        "op, a, b, o", [
            (alu.ALUOp.ADD, 1, 1, 2),
            (alu.ALUOp.ADD, 1, 2, 3),
            (alu.ALUOp.ADD, 2, 1, 3),
            (alu.ALUOp.ADD, 258, 203, 461),
            (alu.ALUOp.ADD, 5, 0, 5),
            (alu.ALUOp.ADD, 0, 5, 5),
            (alu.ALUOp.ADD, 2**32 - 1, 1, 0),

            (alu.ALUOp.SUB, 1, 1, 0),
            (alu.ALUOp.SUB, 4942, 0, 4942),
            (alu.ALUOp.SUB, 1, 2, 2**32 - 1),

            (alu.ALUOp.AND, 0b1111, 0b1111, 0b1111),
            (alu.ALUOp.AND, 0b1111, 0b0000, 0b0000),
            (alu.ALUOp.AND, 0b1010, 0b1010, 0b1010),

            (alu.ALUOp.OR, 0b1010, 0b0101, 0b1111),
            (alu.ALUOp.OR, 0b1111, 0b0000, 0b1111),
            (alu.ALUOp.OR, 0b0000, 0b0000, 0b0000),
            (alu.ALUOp.OR, 0b1001, 0b1001, 0b1001),

            (alu.ALUOp.XOR, 0b1001, 0b1001, 0b0000),
            (alu.ALUOp.XOR, 0b1010, 0b0101, 0b1111),
            (alu.ALUOp.XOR, 0b0000, 0b0000, 0b0000),

            (alu.ALUOp.SLL, 1, 0b1111, 0b11110),
            (alu.ALUOp.SLL, 3, 0b010101, 0b010101000),
            (alu.ALUOp.SLL, 1, 2**32 - 1, 2**32 - 2),

            (alu.ALUOp.SRL, 1, 0b1111, 0b0111),
            (alu.ALUOp.SRL, 5, 0b1111, 0),

            (alu.ALUOp.SRA, 1, 0b1111, 0b0111),
            (alu.ALUOp.SRA,
                1,
                0b10001111000011110000111100001111,
                0b11000111100001111000011110000111)])
def test_alu(comb_sim, op, a, b, o):
    alu_inst = alu.ALU(32)

    def testbench():
        yield alu_inst.op.eq(op)
        yield alu_inst.a.eq(a)
        yield alu_inst.b.eq(b)
        yield nmigen.sim.Settle()
        assert (yield alu_inst.o) == o

    comb_sim(alu_inst, testbench)
