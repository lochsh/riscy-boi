"""The CPU"""
import nmigen as nm

from . import alu
from . import instruction_decoder
from . import program_counter
from . import register_file


class CPU(nm.Elaboratable):
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

    def elaborate(self, _):
        m = nm.Module()

        alu_inst = m.submodules.alu = alu.ALU(32)
        idec = m.submodules.idec = instruction_decoder.InstructionDecoder()
        pc = m.submodules.pc = program_counter.ProgramCounter()
        rf = m.submodules.rf = register_file.RegisterFile(
                debug_reg=self.debug_reg)

        m.d.comb += [
                rf.read_select_1.eq(idec.rf_read_select_1),
                rf.read_select_2.eq(idec.rf_read_select_2),
                rf.write_enable.eq(idec.rf_write_enable),
                rf.write_select.eq(idec.rf_write_select),

                alu_inst.a.eq(idec.alu_imm),
                alu_inst.op.eq(idec.alu_op),

                self.dmem_r_addr.eq(alu_inst.o),

                pc.load.eq(idec.pc_load),
                pc.input_address.eq(alu_inst.o),

                self.imem_addr.eq(pc.pc_next),
                idec.instr.eq(self.imem_data),

                self.debug_out.eq(rf.debug_out),
        ]

        with m.Switch(idec.rd_mux_op):
            with m.Case(instruction_decoder.RdValue.PC_INC):
                m.d.comb += rf.write_data.eq(pc.pc_inc)
            with m.Case(instruction_decoder.RdValue.ALU_OUTPUT):
                m.d.comb += rf.write_data.eq(alu_inst.o)
            with m.Case(instruction_decoder.RdValue.LOAD):
                m.d.comb += rf.write_data.eq(self.dmem_r_data)

        with m.Switch(idec.alu_mux_op):
            with m.Case(instruction_decoder.ALUInput.READ_DATA_1):
                m.d.comb += alu_inst.b.eq(rf.read_data_1)
            with m.Case(instruction_decoder.ALUInput.PC):
                m.d.comb += alu_inst.b.eq(pc.pc)

        return m
