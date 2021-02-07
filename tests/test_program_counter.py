"""Program Counter tests"""
import os

import nmigen.sim

from riscy_boi import program_counter


def run_test(pc, testbench, filename):
    sim = nmigen.sim.Simulator(pc)
    sim.add_sync_process(testbench)
    sim.add_clock(1/10e6)
    with sim.write_vcd(os.path.join("tests", "vcd", filename)):
        sim.run()


def test_program_counter_increment():
    pc = program_counter.ProgramCounter()

    def testbench():
        start = (yield pc.o)
        yield pc.load.eq(0)
        yield
        assert (yield pc.o) == start + program_counter.INSTR_BYTES

    run_test(pc, testbench, "pc-inc.vcd")


def test_program_counter_set():
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.i.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.o) == address

    run_test(pc, testbench, "pc-set.vcd")


def test_program_counter_sequence():
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.i.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.o) == address

        yield pc.load.eq(0)
        yield
        assert (yield pc.o) == address + program_counter.INSTR_BYTES

    run_test(pc, testbench, "pc-seq.vcd")
