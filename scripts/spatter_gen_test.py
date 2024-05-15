import os
import argparse

from util import spatter


@spatter
def run_spatter_test(trace_path):
    import m5

    from m5.objects import Root, DDR4_2400_8x8

    from gem5.components.boards.test_board import TestBoard
    from gem5.components.memory.memory import ChanneledMemory

    from components.spatter_generator import SpatterGenerator

    memory = ChanneledMemory(DDR4_2400_8x8, 1, 128, size="16GiB")

    generator = SpatterGenerator(1, 0, memory.get_size(), trace_path)

    board = TestBoard(
        clk_freq="4GHz",
        generator=generator,
        cache_hierarchy=None,
        memory=memory,
    )

    root = Root(full_system=False, system=board)

    board._pre_instantiate()
    m5.instantiate()

    generator.start_traffic()
    print("Beginning simulation!")

    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}.")


def get_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_path", type=str, help="Path to the trace file.")

    args = parser.parse_args()

    return [args.trace_path]


if __name__ == "__m5_main__":
    run_spatter_test(*get_inputs())
