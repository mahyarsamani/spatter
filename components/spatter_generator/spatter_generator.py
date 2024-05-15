# Copyright (c) 2021 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json

from pathlib import Path
from typing import List, Optional, Tuple, Union

from m5.objects import Addr, SpatterKernelType, SrcClockDomain, VoltageDomain
from gem5.utils.override import overrides
from gem5.components.processors.abstract_generator import (
    AbstractGenerator,
)

from .spatter_kernel import SpatterKernel
from .spatter_generator_core import SpatterGeneratorCore


def parse_kernel(kernel: dict) -> Tuple[int, int, str, List]:
    delta = kernel.get("delta", 0)
    count = kernel.get("count", 1)
    type = kernel.get("kernel", None)
    type = "scatter"
    if type is None:
        raise ValueError(f"Keyword 'kernel' not found.")
    type = SpatterKernelType(type.lower())
    trace = kernel.get("pattern", [])
    if len(trace) == 0:
        raise ValueError(f"Empty 'pattern' found.")
    return (delta, count, type, trace)


def partition_trace(trace: List[int], num_cores: int) -> List[List[int]]:
    partition_size = len(trace) // num_cores
    return [
        trace[i : i + partition_size]
        for i in range(0, len(trace), partition_size)
    ]


class SpatterGenerator(AbstractGenerator):
    def __init__(
        self,
        num_cores: int,
        base_indexer_addr: Addr,
        base_values_addr: Addr,
        trace_path: Union[str, Path],
        clk_freq: Optional[str] = None,
    ) -> None:
        super().__init__(
            cores=self._create_cores(
                num_cores, base_indexer_addr, base_values_addr
            )
        )
        if not clk_freq is None:
            print("clk_freq is not None")
            clock_domain = SrcClockDomain(
                clock=clk_freq, voltage_domain=VoltageDomain()
            )
            self.generator.clk_domain = clock_domain
        with open(trace_path, "r") as trace_file:
            self._trace = json.load(trace_file)

        for index, kernel in enumerate(self._trace):
            try:
                parse_kernel(kernel)
                delta, count, type, trace = parse_kernel(kernel)
                traces = partition_trace(trace, num_cores)
                for core, trace in zip(self.cores, traces):
                    core.add_kernel(
                        SpatterKernel(index, delta, count, type, trace)
                    )
            except ValueError as v:
                print(f"Error parsing kernel {index}: {v}")

    def _create_cores(
        self, num_cores: int, base_indexer_addr: Addr, base_values_addr: Addr
    ) -> List[SpatterGeneratorCore]:
        return [
            SpatterGeneratorCore(base_indexer_addr, base_values_addr)
            for _ in range(num_cores)
        ]

    @overrides(AbstractGenerator)
    def start_traffic(self) -> None:
        for core in self.cores:
            core.start_traffic()
