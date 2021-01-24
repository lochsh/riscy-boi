"""Reigster file"""
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
        self.num_registers = num_registers
        self.register_width = register_width

        self.read_select_1 = nm.Signal(range(self.num_registers))
        self.read_select_2 = nm.Signal(range(self.num_registers))
        self.read_data_1 = nm.Signal(self.register_width)
        self.read_data_2 = nm.Signal(self.register_width)

        self.write_enable = nm.Signal()
        self.write_select = nm.Signal(self.register_width)
        self.write_data = nm.Signal(self.register_width)

    def elaborate(self, _):
        m = nm.Module()
        registers = nm.Memory(
                width=self.register_width,
                depth=self.num_registers)

        # In iCE40 block RAMs are always read-before-write
        rp1 = m.submodules.rp1 = registers.read_port(transparent=False)
        rp2 = m.submodules.rp2 = registers.read_port(transparent=False)
        wp = m.submodules.wp = registers.write_port()

        # The first register, x0, has a special function: Reading it always
        # returns 0 and writes to it are ignored.
        # https://github.com/riscv/riscv-asm-manual/blob/master/riscv-asm.md
        m.d.comb += wp.en.eq(
                nm.Mux(self.write_select == 0, 0, self.write_enable))

        for sel, data, port in zip(
                (self.read_select_1, self.read_data_1, rp1),
                (self.read_select_2, self.read_data_2, rp2),
                (self.write_select, self.write_data, wp)):
            m.d.comb += [port.addr.eq(sel), port.data.eq(data)]

        return m
