"""The CPU"""
import migen as nm

from . import alu
from . import data_memory
from . import instruction_decoder
from . import program_counter
from . import register_file


class CPU(nm.Module):
    """rv32i CPU"""

    def __init__(self, debug_reg=2):
        self.imem_addr = nm.Signal(32)
        self.imem_data = nm.Signal(32)

        self.dmem_r_addr = nm.Signal(32)
        self.dmem_r_data = nm.Signal(32)
        self.dmem_w_addr = nm.Signal(32)
        self.dmem_w_data = nm.Signal(32)

        self.debug_reg = debug_reg
        self.debug_out = nm.Signal(32)

        alu_inst = self.submodules.alu = alu.ALU(32)
        dmem = self.submodules.dmem = data_memory.DataMemory()
        idec = self.submodules.idec = instruction_decoder.InstructionDecoder()
        pc = self.submodules.pc = program_counter.ProgramCounter()
        rf = self.submodules.rf = register_file.RegisterFile(
                debug_reg=self.debug_reg)

        self.comb += [
                rf.read_select_1.eq(idec.rf_read_select_1),
                rf.read_select_2.eq(idec.rf_read_select_2),
                rf.write_enable.eq(idec.rf_write_enable),
                rf.write_select.eq(idec.rf_write_select),

                alu_inst.a.eq(idec.alu_imm),
                alu_inst.op.eq(idec.alu_op),

                self.dmem_r_addr.eq(dmem.dmem_r_addr),
                dmem.byte_address.eq(alu_inst.o),
                dmem.signed.eq(idec.dmem_signed),
                dmem.address_mode.eq(idec.dmem_address_mode),
                dmem.dmem_r_data.eq(self.dmem_r_data),

                pc.load.eq(idec.pc_load),
                pc.input_address.eq(alu_inst.o),

                self.imem_addr.eq(pc.pc_next),
                idec.instr.eq(self.imem_data),

                self.debug_out.eq(rf.debug_out),
        ]

        with self.Switch(idec.rd_mux_op):
            with self.Case(instruction_decoder.RdValue.PC_INC):
                self.comb += rf.write_data.eq(pc.pc_inc)
            with self.Case(instruction_decoder.RdValue.ALU_OUTPUT):
                self.comb += rf.write_data.eq(alu_inst.o)
            with self.Case(instruction_decoder.RdValue.LOAD):
                self.comb += rf.write_data.eq(dmem.load_value)

        with self.Switch(idec.alu_mux_op):
            with self.Case(instruction_decoder.ALUInput.READ_DATA_1):
                self.comb += alu_inst.b.eq(rf.read_data_1)
            with self.Case(instruction_decoder.ALUInput.PC):
                self.comb += alu_inst.b.eq(pc.pc)
