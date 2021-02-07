"""ALU tests"""
import nmigen.sim
import pytest

from riscy_boi import alu


@pytest.mark.parametrize(
        "op, a, b, o", [
            (alu.ALUOp.ADD, 1, 1, 2),
            (alu.ALUOp.ADD, 1, 2, 3),
            (alu.ALUOp.ADD, 2, 1, 3),
            (alu.ALUOp.ADD, 258, 203, 461),
            (alu.ALUOp.ADD, 5, 0, 5),
            (alu.ALUOp.ADD, 0, 5, 5),
            (alu.ALUOp.ADD, 2**32 - 1, 1, 0),
            (alu.ALUOp.SUB, 1, 1, 0),
            (alu.ALUOp.SUB, 4942, 0, 4942),
            (alu.ALUOp.SUB, 1, 2, 2**32 - 1)])
def test_alu(op, a, b, o):
    alu_inst = alu.ALU(32)

    def testbench():
        yield alu_inst.op.eq(op)
        yield alu_inst.a.eq(a)
        yield alu_inst.b.eq(b)
        yield nmigen.sim.Settle()
        assert (yield alu_inst.o) == o

    sim = nmigen.sim.Simulator(alu_inst)
    sim.add_process(testbench)
    with sim.write_vcd("tests/vcd/alu.vcd"):
        sim.run_until(100e-6)
