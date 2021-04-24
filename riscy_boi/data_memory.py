"""Data memory interface"""
import enum

import nmigen as nm


class AddressMode(enum.IntEnum):
    """Address mode for data memory"""
    BYTE = 0b00
    HALF = 0b01
    WORD = 0b10


class DataMemory(nm.Elaboratable):
    """
    Data memory interface

    * byte_address (in): the byte address to read from the data memory
    * address_mode (in): whether the output is byte, half-word or word
    * signed (in): whether to sign- or zero-extend output

    * load_value (out): the value read from the data memory, sliced according
      to address mode
    """

    def __init__(self):
        # Inputs
        self.byte_address = nm.Signal(32)
        self.address_mode = nm.Signal(AddressMode)
        self.signed = nm.Signal()
        self.dmem_r_data = nm.Signal(32)

        # Outputs
        self.dmem_r_addr = nm.Signal(30)
        self.load_value = nm.Signal(32)

    def elaborate(self, _):
        m = nm.Module()
        m.d.comb += self.dmem_r_addr.eq(self.byte_address[2:])

        with m.Switch(self.address_mode):
            with m.Case(AddressMode.BYTE):
                m.d.comb += self.load_value.eq(self.dmem_r_data.word_select(
                    self.byte_address[0:2], 8))
            with m.Case(AddressMode.HALF):
                m.d.comb += self.load_value.eq(self.dmem_r_data.word_select(
                    self.byte_address[1], 16))
            with m.Case(AddressMode.WORD):
                m.d.comb += self.load_value.eq(self.dmem_r_data)

        return m
