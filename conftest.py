"""Test configuration"""
import os
import shutil

import migen.sim
import pytest


VCD_TOP_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tests", "vcd")


def vcd_path(node):
    directory = os.path.join(VCD_TOP_DIR, node.fspath.basename.split(".")[0])
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, node.name + ".vcd")


@pytest.fixture(scope="session", autouse=True)
def clear_vcd_directory():
    shutil.rmtree(VCD_TOP_DIR, ignore_errors=True)


@pytest.fixture
def comb_sim(request):
    def run(fragment, process):
        sim = migen.sim.Simulator(fragment)
        sim.add_process(process)
        with sim.write_vcd(vcd_path(request.node)):
            sim.run_until(100e-6)

    return run


@pytest.fixture
def sync_sim(request):
    def run(fragment, process):
        sim = migen.sim.Simulator(fragment)
        sim.add_sync_process(process)
        sim.add_clock(1 / 10e6)
        with sim.write_vcd(vcd_path(request.node)):
            sim.run()

    return run
