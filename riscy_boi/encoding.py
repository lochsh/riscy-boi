"""Instruction encoding and decoding"""
import enum

import nmigen as nm

OPCODE_START = 0
OPCODE_END = 7
RD_START = 7
RD_END = 12
RS1_START = 15
RS1_END = 20
RS2_START = 20
RS2_END = 25


def sext(immediate, desired_length=32):
    """Sign extension"""
    return nm.Cat(
            immediate,
            nm.Repl(immediate[-1], desired_length - len(immediate)))


def opcode(instruction):
    return instruction[0:7]


def rd(instruction):
    return instruction[7:12]


def rs1(instruction):
    return instruction[15:20]


def rs2(instruction):
    return instruction[20:25]


class Opcode(enum.IntEnum):
    """Instruction opcodes, see page 104 Risc V Spec v2.2"""
    OP_IMM   = 0b0010011  # noqa: E221
    LUI      = 0b0110111  # noqa: E221
    AUIPC    = 0b0010111  # noqa: E221
    OP       = 0b0110011  # noqa: E221
    JAL      = 0b1101111  # noqa: E221
    JALR     = 0b1100111  # noqa: E221
    BRANCH   = 0b1100011  # noqa: E221
    LOAD     = 0b0000011  # noqa: E221
    STORE    = 0b0100011  # noqa: E221
    MISC_MEM = 0b0001111  # noqa: E221
    SYSTEM   = 0b1110011  # noqa: E221


class IntRegImmFunct(enum.IntEnum):
    """Funct field values for integer register-immediate instructions"""
    ADDI         = 0b000  # noqa: E221
    SLTI         = 0b010  # noqa: E221
    SLTIU        = 0b011  # noqa: E221
    XORI         = 0b100  # noqa: E221
    ORI          = 0b110  # noqa: E221
    ANDI         = 0b111  # noqa: E221
    SLLI         = 0b001  # noqa: E221
    SRLI_OR_SRAI = 0b101  # noqa: E221


class IType:
    """I-type instruction format"""
    IMM_START = 20
    IMM_END = 32
    FUNCT_START = 12
    FUNCT_END = 14

    def __init__(self, instruction):
        self.instr = instruction

    @classmethod
    def encode(cls, imm_val, rs1_val, funct_val, rd_val, opcode_val):
        return ((imm_val << cls.IMM_START) |
                (rs1_val << RS1_START) |
                (funct_val << cls.FUNCT_START) |
                (rd_val << RD_START) |
                (opcode_val << OPCODE_START))

    def immediate(self):
        return sext(self.instr[self.IMM_START:self.IMM_END])

    def funct(self):
        return self.instr[self.FUNCT_START:self.FUNCT_END]


class JType:
    """J-type instruction format"""
    IMM_START = 12
    IMM_END = 32
    OPCODE = Opcode.JAL  # The only opcode in rv32i with J-type format

    def __init__(self, instruction):
        self.instr = instruction

    @classmethod
    def encode(cls, imm_val, rd_val):
        return ((imm_val << cls.IMM_START) |
                (rd_val << RD_START) |
                (cls.OPCODE << OPCODE_START))

    def immediate(self):
        unshuffled = nm.Cat(
                self.instr[31],
                self.instr[12:20],
                self.instr[20],
                self.instr[21:31])
        return sext(unshuffled)
