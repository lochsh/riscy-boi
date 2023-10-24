"""Entry point"""
from migen_boards import blackice_ii

from . import top


def main():
    plat = blackice_ii.BlackIceIIPlatform()
    top_inst = top.Top()
    plat.build(top_inst)


if __name__ == "__main__":
    main()
