"""Register file tests"""
import migen as nm

from riscy_boi import register_file


def test_write_to_read_register(sync_sim):
    m = nm.Module()
    rf = m.submodules.rf = register_file.RegisterFile()

    m.comb += [
            rf.write_enable.eq(1),
            rf.write_select.eq(2),
            rf.read_select_1.eq(2),
            rf.write_data.eq(rf.read_data_1 + 1),
    ]

    def testbench():
        expected_value = 10
        for _ in range(expected_value):
            yield

        assert (yield rf.read_data_1) == expected_value

    sync_sim(m, testbench)
