"""Register file"""
import migen as nm


class RegisterFile(nm.Module):
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

    def __init__(self, num_registers=32, register_width=32, debug_reg=2):
        self.num_registers = num_registers
        self.register_width = register_width

        self.read_select_1 = nm.Signal(range(self.num_registers))
        self.read_select_2 = nm.Signal(range(self.num_registers))
        self.read_data_1 = nm.Signal(self.register_width)
        self.read_data_2 = nm.Signal(self.register_width)

        self.write_enable = nm.Signal()
        self.write_select = nm.Signal(self.register_width)
        self.write_data = nm.Signal(self.register_width)

        self.debug_out = nm.Signal(self.register_width)
        self.debug_reg = debug_reg

        registers = nm.Memory(
                width=self.register_width,
                depth=self.num_registers)

        rp1 = self.submodules.rp1 = registers.read_port(domain="comb")
        rp2 = self.submodules.rp2 = registers.read_port(domain="comb")
        debug_rp = self.submodules.debug_rp = registers.read_port(domain="comb")
        wp = self.submodules.wp = registers.write_port(domain="sync")

        # The first register, x0, has a special function: Reading it always
        # returns 0 and writes to it are ignored.
        # https://github.com/riscv/riscv-asm-manual/blob/master/riscv-asm.md
        self.comb += wp.en.eq(
                nm.Mux(self.write_select == 0, 0, self.write_enable))

        self.comb += [
                rp1.addr.eq(self.read_select_1),
                rp2.addr.eq(self.read_select_2),
                wp.addr.eq(self.write_select),
                debug_rp.addr.eq(self.debug_reg),
                self.read_data_1.eq(rp1.data),
                self.read_data_2.eq(rp2.data),
                wp.data.eq(self.write_data),
                self.debug_out.eq(debug_rp.data),
        ]
