"""Instruction decoder"""
import nmigen as nm

from . import alu

OPCODE_POS = 0
OPCODE_LEN = 7
RD_POS = 7
RD_LEN = 5
RS1_POS = 15
RS1_LEN = 5
RS2_POS = 20
RS2_LEN = 5

# Page 104 Risc V Spec v2.2
INTEGER_REGISTER_IMMEDIATE = 0b0010011
INTEGER_REGISTER_REGISTER = 0b0110011
JAL = 0b1101111


def sext(immediate, desired_length=32):
    """Sign extension"""
    return nm.Cat(
            immediate,
            nm.Repl(immediate[-1], desired_length - len(immediate)))


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

        opcode = self.instr[OPCODE_POS:OPCODE_POS + OPCODE_LEN]
        rd = self.instr[RD_POS:RD_POS + RD_LEN]
        rs1 = self.instr[RS1_POS:RS1_POS + RS1_LEN]
        rs2 = self.instr[RS2_POS:RS2_POS + RS2_LEN]

        m.d.comb += self.rf_write_select.eq(rd)
        m.d.comb += self.rf_read_select_1.eq(rs1)
        m.d.comb += self.rf_read_select_2.eq(rs2)

        with m.If(opcode == INTEGER_REGISTER_IMMEDIATE):
            m.d.comb += self.rf_write_enable.eq(1)
            funct = self.instr[12:14]
            imm = self.instr[20:]

            with m.If(funct == 0b000):  # ADDI
                m.d.comb += self.pc_load.eq(0)
                m.d.comb += self.alu_op.eq(alu.ALUOp.ADD)
                m.d.comb += self.alu_imm.eq(sext(imm))

        return m
