import json
import argparse

from util import spatter


@spatter
def run_spatter_test(trace_path, num_cores):
    import m5

    from m5.objects import Root

    from gem5.components.boards.test_board import TestBoard
    from gem5.components.memory import SingleChannelDDR4_2400
    from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
        PrivateL1CacheHierarchy,
    )

    from gem5.components.processors.spatter_gen import (
        SpatterKernel,
        SpatterGenerator,
        parse_kernel,
        partition_trace,
    )

    memory = SingleChannelDDR4_2400(size="32GiB")
    generator = SpatterGenerator(num_cores)

    board = TestBoard(
        clk_freq="4GHz",
        generator=generator,
        cache_hierarchy=PrivateL1CacheHierarchy(
            l1i_size="32KiB", l1d_size="64KiB"
        ),
        memory=memory,
    )

    trace = None
    with open(trace_path, "r") as trace_file:
        kernels = json.load(trace_file)

    for i, kernel in enumerate(kernels):
        delta, count, type, og_trace = parse_kernel(kernel)
        traces = partition_trace(og_trace, num_cores, 128)
        for j, trace in enumerate(traces):
            kernel = SpatterKernel(
                kernel_id=i,
                kernel_delta=delta,
                kernel_count=count,
                kernel_type=type,
                kernel_trace=trace,
                index_size=4,
                base_index_addr=0,
                value_size=8,
                base_value_addr=memory.get_size(),
            )
            generator.cores[j].add_kernel(kernel)

    root = Root(full_system=False, system=board)

    board._pre_instantiate()
    m5.instantiate()

    print("Starting traffic!")
    generator.start_traffic()
    print("Beginning simulation!")

    expected_exit_count = num_cores
    while True:
        exit_event = m5.simulate()
        print(f"Exiting @ tick {m5.curTick()} due to: {exit_event.getCause()}")
        if "done generating requests." in exit_event.getCause():
            expected_exit_count -= 1
        if expected_exit_count == 0:
            break
        m5.stats.dump()


def get_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_path", type=str, help="Path to the trace file.")
    parser.add_argument(
        "num_cores", type=int, help="Number of SpatterGen cores."
    )
    args = parser.parse_args()

    return [args.trace_path, args.num_cores]


if __name__ == "__m5_main__":
    run_spatter_test(*get_inputs())
