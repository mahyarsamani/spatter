# SpatterGen

This is a readme explaining how to use the SpatterGen clocked object to replay
the spatter traces as shown in this
[example from hpcgarage](https://github.com/hpcgarage/spatter/blob/main/standard-suite/app-traces/amg.json).

To run your tests, you need the following:

* Compiled gem5 binary with SpatterGen code.
The submodule in under gem5 in this repository has the code for SpatterGen.
You still need to compile gem5 after cloning.
* \[Optional\] Compiled gem5 binary with SpatterGen component in gem5's stdlib.
The submodule in under gem5 in this repository stdlib components for SpatterGen.
You still need to compile gem5 after cloning.
* gem5 configuration script to setup a system of SpatterGen with memory subsystem.
The script under `scripts/spatter_gen_test.py` sets up a system with SpatterGen
cores, private l1 cache hierarchy, and a single channel DDR4 memory.
* Spatter trace to drive the accesses to the memory system.
`trace.json` is an example trace that can be used for the tests.

The following sections explain how to [download the submodules] for this repo,
[compile gem5](#compiling-gem5) and [run the tests](#running-the-tests).

## Downloading Submodules

To download the submodules in this repository run the following commands after
cloning this repository.

```sh
git submodule init
git submodule update
```

## Compiling gem5

You can refer to the [official gem5 website](https://www.gem5.org/documentation/general_docs/building#dependencies)
for instructions on what dependencies are required as well as how to build gem5.

After installing the required dependencies, you can run the following
command to build gem5.

```sh
scons build/NULL/gem5.opt -j $(nproc)
```

After running this command you should have the gem5 binary under
`gem5/build/NULL/gem5.opt`

## Running the Tests

The script under `scripts/spatter_gen_test.py` takes two inputs.
Below shows the expected output if you don't pass anything to the script.

```sh
$ ./gem5/build/NULL/gem5.opt scripts/spatter_gen_test.py

gem5 Simulator System.  https://www.gem5.org
gem5 is copyrighted software; use the --copyright option for details.

gem5 version DEVELOP-FOR-24.0
gem5 compiled May 31 2024 18:29:21
gem5 started Jun  3 2024 16:50:05
gem5 executing on cascade, pid 2533478
command line: ./gem5/build/NULL/gem5.opt scripts/spatter_gen_test.py

usage: spatter_gen_test.py [-h] trace_path num_cores
spatter_gen_test.py: error: the following arguments are required: trace_path, num_cores
```

You will need to pass two inputs to this script, `trace_path` and `num_cores`.
`trace_path` should be the path to your spatter trace JSON file.
`num_core` denotes the number of SpatterGen cores to instantiate to drive the
memory system.
The script under `scripts/spatter_gen_test.py` will interleaving the pattern
of every kernel between the SpatterGen cores.
**NOTE**: The scripts will configure the system such that each SpatterGen core
will have its own private l1 cache.
The caches are kept coherent.
Below is the code snippet that does that.

```python
    generator = SpatterGenerator(num_cores)

    trace = None
    with open(trace_path, "r") as trace_file:
        kernels = json.load(trace_file)

    for i, kernel in enumerate(kernels):
        delta, count, type, og_trace = parse_kernel(kernel)
        traces = partition_trace(og_trace, num_cores, 128)
        kernels = []
        for trace in traces:
            kernels.append(
                SpatterKernel(
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
            )
        generator.add_kernel(kernels)
```

The following command will start the simulation using `trace.json` as the spatter
trace and `8` SpatterGen cores.
Underneath the command line you see what the expected out will look like.

```sh
$ ./gem5/build/NULL/gem5.opt scripts/spatter_gen_test.py trace.json 8
gem5 Simulator System.  https://www.gem5.org
gem5 is copyrighted software; use the --copyright option for details.

gem5 version DEVELOP-FOR-24.0
gem5 compiled May 31 2024 18:29:21
gem5 started Jun  3 2024 17:00:56
gem5 executing on cascade, pid 2535412
command line: ./gem5/build/NULL/gem5.opt scripts/spatter_gen_test.py trace.json 8

Global frequency set at 1000000000000 ticks per second
warn: No dot file generated. Please install pydot to generate the dot file and pdf.
src/mem/dram_interface.cc:690: warn: DRAM device capacity (16384 Mbytes) does not match the address range assigned (32768 Mbytes)
Starting traffic!
Beginning simulation!
src/sim/simulate.cc:199: info: Entering event queue @ 0.  Starting simulation...
Exiting @ tick 57863750 due to: SpatterGen system.processor.cores3.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 57863750.  Starting simulation...
Exiting @ tick 58019250 due to: SpatterGen system.processor.cores4.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 58019250.  Starting simulation...
Exiting @ tick 58393250 due to: SpatterGen system.processor.cores5.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 58393250.  Starting simulation...
Exiting @ tick 58587000 due to: SpatterGen system.processor.cores6.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 58587000.  Starting simulation...
Exiting @ tick 59250000 due to: SpatterGen system.processor.cores7.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 59250000.  Starting simulation...
Exiting @ tick 60121750 due to: SpatterGen system.processor.cores0.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 60121750.  Starting simulation...
Exiting @ tick 61291500 due to: SpatterGen system.processor.cores2.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 61291500.  Starting simulation...
Exiting @ tick 61476500 due to: SpatterGen system.processor.cores1.generator done generating requests from SpatterKernel 0.
src/sim/simulate.cc:199: info: Entering event queue @ 61476500.  Starting simulation...
Exiting @ tick 126518250 due to: SpatterGen system.processor.cores4.generator done generating requests from SpatterKernel 1.
src/sim/simulate.cc:199: info: Entering event queue @ 126518250.  Starting simulation...
Exiting @ tick 127698500 due to: SpatterGen system.processor.cores5.generator done generating requests from SpatterKernel 1.
src/sim/simulate.cc:199: info: Entering event queue @ 127698500.  Starting simulation...
Exiting @ tick 128459000 due to: SpatterGen system.processor.cores3.generator done generating requests from SpatterKernel 1.
...
```
