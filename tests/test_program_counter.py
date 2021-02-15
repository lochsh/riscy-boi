"""Program Counter tests"""
from riscy_boi import program_counter


def test_program_counter_increment(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        start = (yield pc.o)
        yield pc.load.eq(0)
        yield
        assert (yield pc.o) == start + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)


def test_program_counter_set(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.i.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.o) == address

    sync_sim(pc, testbench)


def test_program_counter_sequence(sync_sim):
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

    sync_sim(pc, testbench)
