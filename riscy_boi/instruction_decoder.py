"""Instruction decoder"""
import nmigen as nm

from . import alu
from . import encoding


class InstructionDecoder(nm.Elaboratable):
    """
    Instruction decoder

    * instr (in): instruction to decode

    * pc_load (out): load signal to program counter
    * alu_op (out): ALU operation to perform
    * alu_imm (out): the value to input to the ALU, constructed from the
      immediate value in the instruction
    * rf_write_enable (out): register file's write_enable input
    * rf_write_select (out): register files' write_select input
    * rf_read_select_1 (out): register file's read_select_1 input
    * rf_read_select_2 (out): register file's read_select_2 input
    """

    def __init__(self, num_registers=32):
        self.instr_width = 32
        self.instr = nm.Signal(self.instr_width)

        self.pc_load = nm.Signal()
        self.alu_op = nm.Signal()
        self.alu_imm = nm.Signal(self.instr_width)
        self.rf_write_enable = nm.Signal()
        self.rf_write_select = nm.Signal(range(num_registers))
        self.rf_read_select_1 = nm.Signal(range(num_registers))
        self.rf_read_select_2 = nm.Signal(range(num_registers))

    def elaborate(self, _):
        m = nm.Module()

        opcode = encoding.opcode(self.instr)
        m.d.comb += self.rf_write_select.eq(encoding.rd(self.instr))
        m.d.comb += self.rf_read_select_1.eq(encoding.rs1(self.instr))
        m.d.comb += self.rf_read_select_2.eq(encoding.rs2(self.instr))

        with m.Switch(opcode):
            with m.Case(encoding.Opcode.OP_IMM):
                m.d.comb += self.rf_write_enable.eq(1)

                itype = encoding.IType(self.instr)
                with m.Switch(itype.funct()):
                    with m.Case(encoding.IntRegImmFunct.ADDI):
                        m.d.comb += self.pc_load.eq(0)
                        m.d.comb += self.alu_op.eq(alu.ALUOp.ADD)
                        m.d.comb += self.alu_imm.eq(itype.immediate())

            with m.Case(encoding.Opcode.JAL):
                m.d.comb += self.rf_write_enable.eq(1)

                jtype = encoding.JType(self.instr)
                m.d.comb += self.pc_load.eq(1)
                m.d.comb += self.alu_op.eq(alu.ALUOp.ADD)
                m.d.comb += self.alu_imm.eq(jtype.immediate())

        return m
