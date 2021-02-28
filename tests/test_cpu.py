"""CPU tests"""
import nmigen as nm

from riscy_boi import cpu, encoding


def test_cpu(sync_sim):
    m = nm.Module()
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
               encoding.JType.encode(0x1ffffc, link_reg)]

    imem = nm.Memory(width=32, depth=1024, init=program)
    imem_rp = m.submodules.imem_rp = imem.read_port(domain="sync")
    m.d.comb += [
            imem_rp.addr.eq(cpu_inst.imem_addr[2:]),
            cpu_inst.imem_data.eq(imem_rp.data),
    ]

    def testbench():
        for _ in range(20):
            yield

    sync_sim(m, testbench)
