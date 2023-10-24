"""Arithmetic Logic Unit"""
import enum

import migen as nm


class ALUOp(enum.IntEnum):
    """Operations for the ALU"""
    ADD = 0b000
    SUB = 0b001
    AND = 0b010
    OR  = 0b011  # noqa: E221
    XOR = 0b100
    SLL = 0b101
    SRL = 0b110
    SRA = 0b111


class ALU(nm.Module):
    """
    Arithmetic Logic Unit

    * op (in): the opcode
    * a (in): the first operand
    * b (in): the second operand

    * o (out): the output
    """

    def __init__(self, width):
        """
        Initialiser

        Args:
            width (int): data width
        """
        self.op = nm.Signal(3)
        self.a = nm.Signal(width)
        self.b = nm.Signal(width)
        self.o = nm.Signal(width)

        shamt_width = 5

        self.comb += nm.Case(
            self.op,
            {
                ALUOp.ADD: self.o.eq(self.a + self.b),
                ALUOp.SUB: self.o.eq(self.a - self.b),
                ALUOp.AND: self.o.eq(self.a & self.b),
                ALUOp.OR: self.o.eq(self.a | self.b),
                ALUOp.XOR: self.o.eq(self.a ^ self.b),
                ALUOp.SLL: self.o.eq(self.b << self.a[:shamt_width]),
                ALUOp.SRL: self.o.eq(self.b >> self.a[:shamt_width]),
                ALUOp.SRA: self.o.eq(self.b >> self.a[:shamt_width]),
            }
        )
