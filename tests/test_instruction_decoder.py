"""Instruction decoder tests"""
import os

import nmigen.sim

from riscy_boi import alu
from riscy_boi import instruction_decoder


def test_decoding_addi():
    idec = instruction_decoder.InstructionDecoder()

    def testbench():
        immediate = 0b100011110000
        opcode = instruction_decoder.INTEGER_REGISTER_IMMEDIATE
        funct = 0
        rs1 = 1
        rd = 2
        instruction = (
                (immediate << 20) |
                (rs1 << instruction_decoder.RS1_POS) |
                (funct << 12) |
                (rd << instruction_decoder.RD_POS) |
                (opcode << instruction_decoder.OPCODE_POS))

        yield idec.instr.eq(instruction)
        yield nmigen.sim.Settle()
        assert (yield idec.pc_load) == 0
        assert (yield idec.rf_read_select_1) == rs1
        assert (yield idec.alu_op) == alu.ALUOp.ADD
        assert (yield idec.alu_imm) == 0b11111111111111111111100011110000

        assert (yield idec.rf_write_enable) == 1
        assert (yield idec.rf_write_select) == rd

    sim = nmigen.sim.Simulator(idec)
    sim.add_process(testbench)
    with sim.write_vcd(os.path.join("tests", "vcd", "idec-addi.vcd")):
        sim.run_until(100e-6)
