"""Top level hardware"""
import migen as nm

from . import cpu
from . import encoding


class Top(nm.Module):
    """Top level"""

    def __init__(self, platform):
        cd_sync = nm.ClockDomain("sync")
        self.domains += cd_sync

        clk100 = platform.request("clk100")
        cd_fast = nm.ClockDomain("fast")
        self.domains += cd_fast
        self.comb += cd_fast.clk.eq(clk100.i)

        self.submodules.pll = nm.Instance(
                "SB_PLL40_CORE",
                p_FEEDBACK_PATH="SIMPLE",
                p_DIVR=3,
                p_DIVF=40,
                p_DIVQ=6,
                p_FILTER_RANGE=2,
                i_RESETB=1,
                i_BYPASS=0,
                i_REFERENCECLK=clk100.i,
                o_PLLOUTCORE=cd_sync.clk)

        reg = 2
        cpu_inst = self.submodules.cpu = cpu.CPU(debug_reg=reg)
        link_reg = 5
        program = [encoding.IType.encode(
                        1,
                        reg,
                        encoding.IntRegImmFunct.ADDI,
                        reg,
                        encoding.Opcode.OP_IMM),
                   # jump back to the previous instruction for infinite loop
                   encoding.JType.encode(0x1ffffc, link_reg)]

        imem = nm.Memory(width=32, depth=256, init=program)
        imem_rp = self.submodules.imem_rp = imem.read_port()
        self.comb += [
                imem_rp.addr.eq(cpu_inst.imem_addr),
                cpu_inst.imem_data.eq(imem_rp.data),
        ]

        dmem = nm.Memory(width=32, depth=256)
        dmem_rp = self.submodules.dmem_rp = dmem.read_port(
                transparent=False,
                domain="fast")
        dmem_wp = self.submodules.dmem_wp = dmem.write_port(domain="fast")
        self.comb += [
                dmem_rp.addr.eq(cpu_inst.dmem_r_addr),
                cpu_inst.dmem_r_data.eq(dmem_rp.data),
                dmem_wp.addr.eq(cpu_inst.dmem_w_addr),
                dmem_wp.data.eq(cpu_inst.dmem_w_data),
        ]

        colours = ["b", "g", "o", "r"]
        leds = nm.Cat(platform.request(f"led_{c}") for c in colours)
        self.sync += leds.eq(cpu_inst.debug_out[13:17])
