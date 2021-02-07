"""Program Counter"""
import enum

import nmigen as nm


INSTR_BYTES = 4


class ProgramCounterOp(enum.IntEnum):
    """Operations for the Program Counter"""
    INC = 0
    SET = 1


class ProgramCounter(nm.Elaboratable):
    """
    Program Counter

    * op (in): the opcode
    * i (in): the input used when setting the address
    * o (out): the address of the next instruction to execute
    """

    def __init__(self, width=32):
        self.op = nm.Signal()
        self.i = nm.Signal(width)
        self.o = nm.Signal(width)
        self.width = width

    def elaborate(self, _):
        m = nm.Module()
        pc = nm.Signal(self.width)

        with m.Switch(self.op):
            with m.Case(ProgramCounterOp.INC):
                m.d.sync += pc.eq(pc + INSTR_BYTES)
                m.d.comb += self.o.eq(pc)
            with m.Case(ProgramCounterOp.SET):
                m.d.sync += pc.eq(self.i + INSTR_BYTES)
                m.d.comb += self.o.eq(self.i)

        return m
