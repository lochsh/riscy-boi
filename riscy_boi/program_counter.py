"""Program Counter"""
import nmigen as nm

INSTR_BYTES = 4


class ProgramCounter(nm.Elaboratable):
    """
    Program Counter

    * load (in): low to increment, high to load an address
    * i (in): the input used when loading an address
    * o (out): the address of the next instruction to execute
    """

    def __init__(self, width=32):
        self.load = nm.Signal()
        self.i = nm.Signal(width)
        self.o = nm.Signal(width)
        self.width = width

    def elaborate(self, _):
        m = nm.Module()
        pc = nm.Signal(self.width)

        # Pylint is confused about this part of nmigen
        # pylint: disable=E1129
        with m.If(self.load):
            m.d.sync += pc.eq(self.i + INSTR_BYTES)
            m.d.comb += self.o.eq(self.i)
        # pylint: disable=E1129
        with m.Else():
            m.d.sync += pc.eq(pc + INSTR_BYTES)
            m.d.comb += self.o.eq(pc)

        return m
