import enum

import nmigen as nm
from nmigen.cli import main


class ALUOp(enum.Enum):
    ADD = 0
    SUB = 1


class ALU(nm.Elaboratable):

    def __init__(self, width):
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


if __name__ == "__main__":
    alu = ALU(width=32)
    main(alu, ports=[alu.op, alu.a, alu.b, alu.o])
