"""Instruction encoding and decoding"""
import collections
import enum
import functools

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
    offset_start = 20
    offset_end = 32
    FUNCT_START = 12
    FUNCT_END = 14

    def __init__(self, instruction):
        self.instr = instruction

    @classmethod
    def encode(cls, imm_val, rs1_val, funct_val, rd_val, opcode_val):
        return ((imm_val << cls.offset_start) |
                (rs1_val << RS1_START) |
                (funct_val << cls.FUNCT_START) |
                (rd_val << RD_START) |
                (opcode_val << OPCODE_START))

    def immediate(self):
        return sext(self.instr[self.offset_start:self.offset_end])

    def funct(self):
        return self.instr[self.FUNCT_START:self.FUNCT_END]


class JType:
    """J-type instruction format"""
    ImmediateField = collections.namedtuple(
            "ImmediateField",
            ["instr_start", "instr_end", "offset_start", "offset_end"],
    )

    IMM_FIELDS = (
            ImmediateField(
                instr_start=12,
                instr_end=20,
                offset_start=12,
                offset_end=20),
            ImmediateField(
                instr_start=20,
                instr_end=21,
                offset_start=11,
                offset_end=12),
            ImmediateField(
                instr_start=21,
                instr_end=31,
                offset_start=1,
                offset_end=11),
            ImmediateField(
                instr_start=31,
                instr_end=32,
                offset_start=20,
                offset_end=21))

    OPCODE = Opcode.JAL  # The only opcode in rv32i with J-type format

    def __init__(self, instruction):
        self.instr = instruction

    @classmethod
    def encode(cls, offset, rd_val):
        unsigned_offset = nm.Const(offset, 32).as_unsigned()

        def shuffle_imm(result, field):
            return result | (
                    unsigned_offset[field.offset_start:field.offset_end]
                    << field.instr_start)
        sorted_imm_fields = sorted(
                cls.IMM_FIELDS,
                key=lambda field: field.instr_start)
        return (functools.reduce(shuffle_imm, sorted_imm_fields, 0) |
                (rd_val << RD_START) |
                (cls.OPCODE << OPCODE_START))

    def immediate(self):
        sorted_imm_fields = sorted(
                self.IMM_FIELDS,
                key=lambda field: field.offset_start)
        to_unshuffle = [self.instr[field.instr_start:field.instr_end]
                        for field in sorted_imm_fields]
        unshuffled = nm.Cat(0, *to_unshuffle)
        return sext(unshuffled)
