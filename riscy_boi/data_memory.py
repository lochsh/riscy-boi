"""Data memory interface"""
import enum

import migen as nm


class AddressMode(enum.IntEnum):
    """Address mode for data memory"""
    BYTE = 0b00
    HALF = 0b01
    WORD = 0b10


class DataMemory(nm.Module):
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

        self.comb += self.dmem_r_addr.eq(self.byte_address[2:])

        with self.Switch(self.address_mode):
            with self.Case(AddressMode.BYTE):
                self.comb += self.load_value.eq(self.dmem_r_data.word_select(
                    self.byte_address[0:2], 8))
            with self.Case(AddressMode.HALF):
                self.comb += self.load_value.eq(self.dmem_r_data.word_select(
                    self.byte_address[1], 16))
            with self.Case(AddressMode.WORD):
                self.comb += self.load_value.eq(self.dmem_r_data)
