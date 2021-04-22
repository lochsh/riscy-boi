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
    """
    Sign extension

    Args:
        immediate (nm.Value): the immediate to be sign extended
        desired_length (int): the desired length of the extended output

    Returns:
        nm.hdl.ast.Cat: the sign-extended immediate
    """
    return nm.Cat(
            immediate,
            nm.Repl(immediate[-1], desired_length - len(immediate)))


def opcode(instruction):
    """
    Extract the opcode from an instruction.

    Note the opcode position is the same for all instructions.

    Args:
        instruction (nm.Signal): the instruction to extract the opcode from

    Returns:
        nm.hdl.ast.Slice: the opcode
    """
    return instruction[OPCODE_START:OPCODE_END]


def rd(instruction):
    """
    Extract the destination register from an instruction.

    Note the destination register field is in the same position for all
    instructions that encode it, but not all instructions do (e.g. S-type
    instructions).

    Args:
        instruction (nm.Signal): the instruction to extract the destination
            register from

    Returns:
        nm.hdl.ast.Slice: the destination register
    """
    return instruction[RD_START:RD_END]


def rs1(instruction):
    """
    Extract the source register 1 field from an instruction.

    Note this field is in the same position for all instructions that encode
    it, but not all instructions do (e.g. U-type instructions).

    Args:
        instruction (nm.Signal): the instruction to extract source register 1
            from

    Returns:
        nm.hdl.ast.Slice: the source register 1 field
    """
    return instruction[RS1_START:RS1_END]


def rs2(instruction):
    """
    Extract the source register 2 field from an instruction.

    Note this field is in the same position for all instructions that encode
    it, but not all instructions do (e.g. I-type instructions).

    Args:
        instruction (nm.Signal): the instruction to extract source register 2
            from

    Returns:
        nm.hdl.ast.Slice: the source register 2 field
    """
    return instruction[RS2_START:RS2_END]


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


class LoadFunct(enum.IntEnum):
    """Funct field values for load instructions"""
    LB  = 0b000  # noqa: E221
    LH  = 0b001  # noqa: E221
    LW  = 0b010  # noqa: E221
    LBU = 0b100
    LHU = 0b101


class RightShiftType(enum.IntEnum):
    """Shift type for distinguishing between SRLI and SRAI instructions"""
    SRLI = 0b0000000
    SRAI = 0b0100000


class IType:
    """I-type instruction format"""
    IMM_START = 20
    IMM_END = 32
    FUNCT_START = 12
    FUNCT_END = 15

    def __init__(self, instruction):
        """
        Initialiser

        Args:
            instruction (nm.Value): the instruction to decode
        """
        self.instr = instruction

    @classmethod
    def encode(cls, imm_val, rs1_val, funct_val, rd_val, opcode_val):
        """
        Assembler method to encode an instruction

        Args:
            imm_val (int): the immediate value
            rs1_val (int): the source register 1 value
            funct_val (IntRegImmFunct): the function field
            rd_val (int): the destination register value
            opcode_val (Opcode): the opcode

        Returns:
            int: the encoded instruction
        """
        return ((imm_val << cls.IMM_START) |
                (rs1_val << RS1_START) |
                (funct_val << cls.FUNCT_START) |
                (rd_val << RD_START) |
                (opcode_val << OPCODE_START))

    def immediate(self):
        """
        Construct the sign-extended immediate from the instruction

        Returns:
            nm.hdl.ast.Cat: the decoded immediate
        """
        return sext(self.instr[self.IMM_START:self.IMM_END])

    def funct(self):
        return self.instr[self.FUNCT_START:self.FUNCT_END]

    def shift_amount(self):
        """For SLLI, SRLI and SRAI instructions, get the shift amount"""
        return self.instr[self.IMM_START:self.IMM_START + 5]

    def right_shift_type(self):
        """For SRLI and SRAI instructions, get the shift type"""
        return self.instr[self.IMM_START + 5:self.IMM_END]


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
        """
        Initialiser

        Args:
            instruction (nm.Value): the instruction to decode
        """
        self.instr = instruction

    @classmethod
    def encode(cls, offset, rd_val):
        """
        Assembler method to encode an instruction

        Args:
            offset (int): the jump offset
            rd_val (int): the destination register

        Returns:
            int: the encoded instruction
        """

        def shuffle_imm(result, field):
            width = field.offset_end - field.offset_start
            mask = int("1" * width, 2) << field.offset_start

            return result | (
                    (offset & mask) <<
                    (field.instr_start - field.offset_start))

        sorted_imm_fields = sorted(
                cls.IMM_FIELDS,
                key=lambda field: field.instr_start)

        return (functools.reduce(shuffle_imm, sorted_imm_fields, 0) |
                (rd_val << RD_START) |
                (cls.OPCODE << OPCODE_START))

    def immediate(self):
        """
        Construct the sign-extended immediate from the instruction

        Returns:
            nm.hdl.ast.Cat: the decoded immediate
        """
        sorted_imm_fields = sorted(
                self.IMM_FIELDS,
                key=lambda field: field.offset_start)

        to_unshuffle = [self.instr[field.instr_start:field.instr_end]
                        for field in sorted_imm_fields]

        unshuffled = nm.Cat(0, *to_unshuffle)
        return sext(unshuffled)
