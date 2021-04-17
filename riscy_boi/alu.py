"""Arithmetic Logic Unit"""
import enum

import nmigen as nm


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


class ALU(nm.Elaboratable):
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
        self.op = nm.Signal(ALUOp)
        self.a = nm.Signal(width)
        self.b = nm.Signal(width)
        self.o = nm.Signal(width)

    def elaborate(self, _):
        m = nm.Module()
        shamt_width = 5

        with m.Switch(self.op):
            with m.Case(ALUOp.ADD):
                m.d.comb += self.o.eq(self.a + self.b)
            with m.Case(ALUOp.SUB):
                m.d.comb += self.o.eq(self.a - self.b)
            with m.Case(ALUOp.AND):
                m.d.comb += self.o.eq(self.a & self.b)
            with m.Case(ALUOp.OR):
                m.d.comb += self.o.eq(self.a | self.b)
            with m.Case(ALUOp.XOR):
                m.d.comb += self.o.eq(self.a ^ self.b)
            with m.Case(ALUOp.SLL):
                m.d.comb += self.o.eq(self.b << self.a[:shamt_width])
            with m.Case(ALUOp.SRL):
                m.d.comb += self.o.eq(self.b >> self.a[:shamt_width])
            with m.Case(ALUOp.SRA):
                m.d.comb += self.o.eq(self.b.as_signed() >>
                                      self.a[:shamt_width])

        return m
