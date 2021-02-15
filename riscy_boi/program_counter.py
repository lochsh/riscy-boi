"""Program Counter"""
import nmigen as nm

INSTR_BYTES = 4


class ProgramCounter(nm.Elaboratable):
    """
    Program Counter

    * load (in): low to increment, high to load an address
    * input_address (in): the input used when loading an address

    * next_value (out): the address of the next instruction to execute
    * incremented (out): the incremented value
    """

    def __init__(self, width=32):
        self.load = nm.Signal()
        self.input_address = nm.Signal(width)
        self.next_value = nm.Signal(width)
        self.incremented = nm.Signal(width)
        self.width = width

    def elaborate(self, _):
        m = nm.Module()

        # Pylint is confused about this part of nmigen
        # pylint: disable=E1129
        with m.If(self.load):
            m.d.sync += self.incremented.eq(self.input_address + INSTR_BYTES)
            m.d.comb += self.next_value.eq(self.input_address)
        # pylint: disable=E1129
        with m.Else():
            m.d.sync += self.incremented.eq(self.incremented + INSTR_BYTES)
            m.d.comb += self.next_value.eq(self.incremented)

        return m
