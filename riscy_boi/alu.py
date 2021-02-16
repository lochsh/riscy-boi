"""Arithmetic Logic Unit"""
import enum

import nmigen as nm


class ALUOp(enum.IntEnum):
    """Operations for the ALU"""
    ADD = 0
    SUB = 1


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
        self.op = nm.Signal()
        self.a = nm.Signal(width)
        self.b = nm.Signal(width)
        self.o = nm.Signal(width)

    def elaborate(self, _):
        m = nm.Module()

        with m.Switch(self.op):
            with m.Case(ALUOp.ADD):
                m.d.comb += self.o.eq(self.a + self.b)
            with m.Case(ALUOp.SUB):
                m.d.comb += self.o.eq(self.a - self.b)
        return m
