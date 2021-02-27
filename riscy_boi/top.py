"""Top level hardware"""
import nmigen as nm

from . import cpu
from . import encoding


class Top(nm.Elaboratable):
    """Top level"""

    def elaborate(self, platform):
        m = nm.Module()

        cd_sync = nm.ClockDomain("sync")
        m.domains += cd_sync
        m.submodules.pll = nm.Instance(
                "SB_PLL40_CORE",
                p_FEEDBACK_PATH="SIMPLE",
                p_DIVR=3,
                p_DIVF=40,
                p_DIVQ=6,
                p_FILTER_RANGE=2,
                i_RESETB=1,
                i_BYPASS=0,
                i_REFERENCECLK=platform.request("clk100").i,
                o_PLLOUTCORE=cd_sync.clk)

        reg = 2
        cpu_inst = m.submodules.cpu = cpu.CPU(debug_reg=reg)
        link_reg = 5
        program = [encoding.IType.encode(
                        1,
                        reg,
                        encoding.IntRegImmFunct.ADDI,
                        reg,
                        encoding.Opcode.OP_IMM),
                   # jump back to the previous instruction for infinite loop
                   encoding.JType.encode(0xffffc, link_reg)]

        imem = nm.Memory(width=32, depth=1024, init=program)
        imem_rp = m.submodules.imem_rp = imem.read_port()
        m.d.comb += [
                imem_rp.addr.eq(cpu_inst.imem_addr),
                cpu_inst.imem_data.eq(imem_rp.data),
        ]

        colours = ["b", "g", "o", "r"]
        leds = nm.Cat(platform.request(f"led_{c}") for c in colours)
        m.d.sync += leds.eq(cpu_inst.debug_out[13:17])

        return m
