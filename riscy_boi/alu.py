import enum
import operator

import nmigen as nm
from nmigen.cli import main


class ALUOp(enum.Enum):
    ADD = 0
    SUB = 1


class Operator(nm.Elaboratable):

    def __init__(self, width, operation):
        self.operation = operation
        self.a = nm.Signal(width)
        self.b = nm.Signal(width)
        self.o = nm.Signal(width)

    def elaborate(self, _):
        m = nm.Module()
        m.d.comb += self.o.eq(self.operation(self.a, self.b))
        return m


class ALU(nm.Elaboratable):

    def __init__(self, width):
        self.op = nm.Signal()
        self.a = nm.Signal(width)
        self.b = nm.Signal(width)
        self.o = nm.Signal(width)

        self.add = Operator(width, operator.add)
        self.sub = Operator(width, operator.sub)

    def elaborate(self, _):
        m = nm.Module()
        m.submodules.add = self.add
        m.submodules.sub = self.sub
        m.d.comb += [
                self.add.a.eq(self.a),
                self.sub.a.eq(self.a),
                self.add.b.eq(self.b),
                self.sub.b.eq(self.b),
        ]

        with m.Switch(self.op):
            with m.Case(ALUOp.ADD):
                m.d.comb += self.o.eq(self.add.o)
            with m.Case(ALUOp.SUB):
                m.d.comb += self.o.eq(self.sub.o)
        return m


if __name__ == "__main__":
    alu = ALU(width=32)
    main(alu, ports=[alu.op, alu.a, alu.b, alu.o])
