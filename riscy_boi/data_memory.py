"""Data memory interface"""
import enum

import nmigen as nm


class AddressMode(enum.IntEnum):
    BYTE = 0b00
    HALF = 0b01
    WORD = 0b10


class DataMemory(nm.Elaboratable):
    """
    Data memory interface

    * read_address (in): the address to read from the data memory
    * address_mode (in): whether the output is byte, half-word or word
    * signed (in): whether to sign- or zero-extend output

    * o (out): the value read from the data memory

    """

    def __init__(self):
        # Inputs
        self.read_address = nm.Signal(32)
        self.address_mode = nm.Signal(AddressMode)
        self.signed = nm.Signal()
        self.dmem_r_data = nm.Signal(32)

        # Outputs
        self.dmem_r_addr = nm.Signal(30)
        self.o = nm.Signal(32)

    def elaborate(self, _):
        m = nm.Module()
        m.d.comb += self.dmem_r_addr.eq(self.read_address[2:])

        with m.Switch(self.address_mode):
            with m.Case(AddressMode.BYTE):
                m.d.comb += self.o.eq(self.dmem_r_data.word_select(
                    self.read_address[0:2], 8))
            with m.Case(AddressMode.HALF):
                m.d.comb += self.o.eq(self.dmem_r_data.word_select(
                    self.read_address[1], 16))
            with m.Case(AddressMode.WORD):
                m.d.comb += self.o.eq(self.dmem_r_data)

        return m
