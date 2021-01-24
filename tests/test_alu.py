"""ALU tests"""
import nmigen.sim

from riscy_boi import alu


def test_alu():
    alu_inst = alu.ALU(32)

    def testbench():
        yield alu_inst.op.eq(alu.ALUOp.ADD)
        yield alu_inst.a.eq(1)
        yield alu_inst.b.eq(1)
        yield nmigen.sim.Settle()
        assert (yield alu_inst.o) == 2

    sim = nmigen.sim.Simulator(alu_inst)
    sim.add_process(testbench)
    with sim.write_vcd("tests/vcd/alu.vcd"):
        sim.run_until(100e-6)
