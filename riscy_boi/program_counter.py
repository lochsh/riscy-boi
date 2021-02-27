"""Program Counter"""
import nmigen as nm

INSTR_BYTES = 4


class ProgramCounter(nm.Elaboratable):
    """
    Program Counter

    * load (in): low to increment, high to load an address
    * input_address (in): the input used when loading an address

    * pc (out): the address of the instruction being executed this clock cycle
    * pc_next (out): the address of the instruction being executed next clock
      cycle
    * pc_inc (out): the address after that of the instruction being executed
      this clock cycle
    """

    def __init__(self, width=32):
        self.load = nm.Signal()
        self.input_address = nm.Signal(width)
        self.pc = nm.Signal(width)
        self.pc_next = nm.Signal(width)
        self.pc_inc = nm.Signal(width)

    def elaborate(self, _):
        m = nm.Module()

        m.d.comb += self.pc_inc.eq(self.pc + INSTR_BYTES)
        m.d.sync += self.pc.eq(self.pc_next)

        with m.If(self.load):
            m.d.comb += self.pc_next.eq(self.input_address)
        with m.Else():
            m.d.comb += self.pc_next.eq(self.pc_inc)

        return m
