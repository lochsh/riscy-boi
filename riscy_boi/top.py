"""Top level hardware"""
import nmigen as nm

from . import cpu


class Top(nm.Elaboratable):
    """Top level"""

    def elaborate(self, platform):
        m = nm.Module()
        cpu_inst = m.submodules.cpu = cpu.CPU()
        imem = nm.Memory(width=32, depth=1024)
        imem_rp = m.submodules.imem_rp = imem.read_port()
        m.d.comb += [
                imem_rp.addr.eq(cpu_inst.imem_addr),
                cpu_inst.imem_data.eq(imem_rp.data),
        ]

        colours = ["b", "g", "o", "r"]
        leds = nm.Cat(platform.request(f"led_{c}") for c in colours)
        m.d.sync += leds.eq(cpu_inst.imem_addr[25:29])

        return m
