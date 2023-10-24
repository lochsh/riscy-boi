"""Instruction decoder"""
import enum


import migen as nm

from . import alu
from . import data_memory
from . import encoding


class RdValue(enum.IntEnum):
    """MUX opcodes for the value put in the destination register"""
    ALU_OUTPUT = 0
    PC_INC = 1
    LOAD = 2


class ALUInput(enum.IntEnum):
    """MUX opcodes for the value inputted to the ALU"""
    READ_DATA_1 = 0
    PC = 1


class InstructionDecoder(nm.Module):
    """
    Instruction decoder

    * instr (in): instruction to decode

    * pc_load (out): load signal to program counter

    * alu_op (out): ALU operation to perform
    * alu_imm (out): the value to input to the ALU, constructed from the
      immediate value in the instruction
    * alu_mux_op (out): multiplexor operator defining what value is the first
      input to the ALU

    * rf_write_enable (out): register file's write_enable input
    * rf_write_select (out): register files' write_select input
    * rf_read_select_1 (out): register file's read_select_1 input
    * rf_read_select_2 (out): register file's read_select_2 input
    * rd_mux_op (out): multiplexor operation defining what value is written to
      the destination register

    * dmem_address_mode (out): address mode for data memory reads
    * dmem_signed (out): whether input to data memory should be sign-extended
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
        self.rd_mux_op = nm.Signal(RdValue)
        self.alu_mux_op = nm.Signal(ALUInput)
        self.dmem_address_mode = nm.Signal(data_memory.AddressMode)
        self.dmem_signed = nm.Signal()

        opcode = encoding.opcode(self.instr)
        self.comb += self.rf_write_select.eq(encoding.rd(self.instr))
        self.comb += self.rf_read_select_1.eq(encoding.rs1(self.instr))
        self.comb += self.rf_read_select_2.eq(encoding.rs2(self.instr))

        with self.Switch(opcode):
            with self.Case(encoding.Opcode.OP_IMM):
                self.comb += self.rf_write_enable.eq(1)

                itype = encoding.IType(self.instr)
                with self.Switch(itype.funct()):
                    self.comb += [
                            self.pc_load.eq(0),
                            self.rd_mux_op.eq(RdValue.ALU_OUTPUT),
                            self.alu_mux_op.eq(ALUInput.READ_DATA_1),
                    ]

                    with self.Case(encoding.IntRegImmFunct.ADDI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.ADD),
                                self.alu_imm.eq(itype.immediate()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.XORI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.XOR),
                                self.alu_imm.eq(itype.immediate()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.ORI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.OR),
                                self.alu_imm.eq(itype.immediate()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.ORI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.OR),
                                self.alu_imm.eq(itype.immediate()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.ANDI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.AND),
                                self.alu_imm.eq(itype.immediate()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.SLLI):
                        self.comb += [
                                self.alu_op.eq(alu.ALUOp.SLL),
                                self.alu_imm.eq(itype.shift_amount()),
                        ]

                    with self.Case(encoding.IntRegImmFunct.SRLI_OR_SRAI):
                        self.comb += self.alu_imm.eq(itype.shift_amount())
                        with self.Switch(itype.right_shift_type()):
                            with self.Case(encoding.RightShiftType.SRLI):
                                self.comb += self.alu_op.eq(alu.ALUOp.SRL)
                            with self.Case(encoding.RightShiftType.SRAI):
                                self.comb += self.alu_op.eq(alu.ALUOp.SRA)

            with self.Case(encoding.Opcode.JAL):
                self.comb += self.rf_write_enable.eq(1)

                jtype = encoding.JType(self.instr)
                self.comb += [
                        self.pc_load.eq(1),
                        self.alu_op.eq(alu.ALUOp.ADD),
                        self.alu_imm.eq(jtype.immediate()),
                        self.rd_mux_op.eq(RdValue.PC_INC),
                        self.alu_mux_op.eq(ALUInput.PC),
                ]

            with self.Case(encoding.Opcode.LOAD):
                self.comb += [
                        self.rf_write_enable.eq(1),
                        self.pc_load.eq(0),
                        self.alu_op.eq(alu.ALUOp.ADD),
                        self.alu_imm.eq(itype.immediate()),
                        self.rd_mux_op.eq(RdValue.LOAD),
                        self.alu_mux_op.eq(ALUInput.READ_DATA_1),
                ]

                itype = encoding.IType(self.instr)
                funct = itype.funct()
                with nm.If(funct == encoding.LoadFunct.LW):
                    self.comb += self.dmem_address_mode.eq(
                            data_memory.AddressMode.WORD)
                with self.Elif((funct == encoding.LoadFunct.LH) |
                            (funct == encoding.LoadFunct.LHU)):
                    self.comb += self.dmem_address_mode.eq(
                                data_memory.AddressMode.HALF)
                with self.Elif((funct == encoding.LoadFunct.LB) |
                            (funct == encoding.LoadFunct.LBU)):
                    self.comb += self.dmem_address_mode.eq(
                                data_memory.AddressMode.BYTE)

                self.comb += self.dmem_signed.eq(funct[2] == 0)
