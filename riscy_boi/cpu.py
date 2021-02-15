"""The CPU"""
import nmigen as nm

from . import alu
from . import instruction_decoder
from . import program_counter
from . import register_file


class CPU(nm.Elaboratable):
    """rv32i CPU"""

    def __init__(self):
        self.imem_addr = nm.Signal(32)
        self.imem_data = nm.Signal(32)

    def elaborate(self, _):
        m = nm.Module()

        alu_inst = m.submodules.alu = alu.ALU(32)
        idec = m.submodules.idec = instruction_decoder.InstructionDecoder()
        pc = m.submodules.pc = program_counter.ProgramCounter()
        rf = m.submodules.rf = register_file.RegisterFile()

        m.d.comb += [
                rf.read_select_1.eq(idec.rf_read_select_1),
                rf.read_select_2.eq(idec.rf_read_select_2),
                rf.write_enable.eq(idec.rf_write_enable),
                rf.write_select.eq(idec.rf_write_select),

                alu_inst.a.eq(rf.read_data_1),
                alu_inst.b.eq(idec.alu_imm),
                alu_inst.op.eq(idec.alu_op),

                pc.load.eq(idec.pc_load),
                pc.input_address.eq(alu_inst.o),

                self.imem_addr.eq(pc.next_value),
                idec.instr.eq(self.imem_data)
        ]

        with m.If(idec.mux_op):
            m.d.comb += rf.write_data.eq(pc.incremented)
        with m.Else():
            m.d.comb += rf.write_data.eq(alu_inst.o)

        return m
