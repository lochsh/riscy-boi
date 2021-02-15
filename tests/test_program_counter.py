"""Program Counter tests"""
from riscy_boi import program_counter


def test_program_counter_increment(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        start = (yield pc.next_value)
        yield pc.load.eq(0)
        yield
        assert (yield pc.next_value) == start + program_counter.INSTR_BYTES
        assert (yield pc.incremented) == start + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)


def test_program_counter_set(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.input_address.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.next_value) == address
        yield
        assert (yield pc.incremented) == (
                0xdeadbeef + program_counter.INSTR_BYTES)

    sync_sim(pc, testbench)


def test_program_counter_sequence(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.input_address.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.next_value) == address
        assert (yield pc.incremented) == program_counter.INSTR_BYTES

        yield pc.load.eq(0)
        yield
        assert (yield pc.next_value) == address + program_counter.INSTR_BYTES
        assert (yield pc.incremented) == address + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)
