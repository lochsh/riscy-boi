"""Test configuration"""
import os

import nmigen.sim
import pytest


def vcd_path(node):
    directory = os.path.join(
            "tests",
            "vcd",
            node.fspath.basename.split(".")[0])
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, node.name + ".vcd")


@pytest.fixture
def comb_sim(request):

    def run(fragment, process):
        sim = nmigen.sim.Simulator(fragment)
        sim.add_process(process)
        with sim.write_vcd(vcd_path(request.node)):
            sim.run_until(100e-6)

    return run


@pytest.fixture
def sync_sim(request):

    def run(fragment, process):
        sim = nmigen.sim.Simulator(fragment)
        sim.add_sync_process(process)
        sim.add_clock(1 / 10e6)
        with sim.write_vcd(vcd_path(request.node)):
            sim.run()

    return run
