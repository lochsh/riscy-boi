"""Program Counter"""
import migen as nm

INSTR_BYTES = 4


class ProgramCounter(nm.Module):
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

        self.comb += self.pc_inc.eq(self.pc + INSTR_BYTES)
        self.sync += self.pc.eq(self.pc_next)

        self.comb += nm.If(
            self.load,
            self.pc_next.eq(self.input_address)).Else(
            self.pc_next.eq(self.pc_inc)
        )
