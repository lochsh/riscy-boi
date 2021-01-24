import nmigen as nm
import nmigen.sim
from riscy_boi import alu


def test_alu():
    alu_inst = alu.ALU(32)
    mod = nm.Module()
    mod.submodules.alu = alu_inst
    o = nm.Signal.like(alu_inst.o)
    mod.d.sync += o.eq(alu_inst.o)

    def testbench():
        yield alu_inst.op.eq(alu.ALUOp.ADD)
        yield alu_inst.a.eq(1)
        yield alu_inst.b.eq(1)
        yield
        yield
        assert (yield o) == 2

    sim = nm.sim.Simulator(mod)
    sim.add_sync_process(testbench)
    sim.add_clock(1e-6)
    with sim.write_vcd("tests/vcd/alu.vcd"):
        sim.run()
