"""Program Counter tests"""
from riscy_boi import program_counter


def test_program_counter_increment(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        yield pc.load.eq(0)
        yield
        curr = (yield pc.pc)
        assert curr == program_counter.INSTR_BYTES
        assert (yield pc.pc_inc) == curr + program_counter.INSTR_BYTES
        assert (yield pc.pc_next) == curr + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)


def test_program_counter_set(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.input_address.eq(address)
        yield pc.load.eq(1)
        yield

        curr = (yield pc.pc)
        assert curr == program_counter.INSTR_BYTES
        assert (yield pc.pc_inc) == curr + program_counter.INSTR_BYTES
        assert (yield pc.pc_next) == address

        yield pc.load.eq(0)
        yield

        assert (yield pc.pc) == address
        assert (yield pc.pc_inc) == address + program_counter.INSTR_BYTES
        assert (yield pc.pc_next) == address + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)


def test_program_counter_sequence(sync_sim):
    pc = program_counter.ProgramCounter()

    def testbench():
        address = 0xdeadbeef
        yield pc.input_address.eq(address)
        yield pc.load.eq(1)
        yield
        assert (yield pc.pc) == program_counter.INSTR_BYTES
        assert (yield pc.pc_inc) == program_counter.INSTR_BYTES * 2
        assert (yield pc.pc_next) == address

        yield pc.load.eq(0)
        yield
        assert (yield pc.pc) == address
        assert (yield pc.pc_inc) == address + program_counter.INSTR_BYTES
        assert (yield pc.pc_next) == address + program_counter.INSTR_BYTES

    sync_sim(pc, testbench)
