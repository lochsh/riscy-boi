import nmigen as nm


class RegisterFile(nm.Elaboratable):
    """
    Register file

    * read_select_1 (in): select which register to read at read_data_1
    * read_select_2 (in): select which register to read at read_data_2
    * read_data_1 (out): value of register selected by read_select_1
    * read_data_2 (out): value of register selected by read_select_2

    * write_enable (in): assert to trigger write to register file
    * write_select (in): select which register to write to
    * write_data (in): data to write to register selected by write_select
    """

    def __init__(self, num_registers=32, register_width=32):
        self.read_select_1 = nm.Signal(range(num_registers))
        self.read_select_2 = nm.Signal(range(num_registers))
        self.read_data_1 = nm.Signal(register_width)
        self.read_data_2 = nm.Signal(register_width)

        self.write_enable = nm.Signal()
        self.write_select = nm.Signal(register_width)
        self.write_data = nm.Signal(register_width)
