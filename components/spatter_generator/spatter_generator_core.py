# Copyright (c) 2024 The Regents of the University of California
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


from m5.objects import Addr, Model, Port

from gem5.utils.override import overrides
from gem5.components.processors.abstract_core import AbstractCore
from gem5.components.processors.abstract_generator_core import (
    AbstractGeneratorCore,
)

from .spatter_kernel import SpatterKernel


class SpatterGeneratorCore(AbstractGeneratorCore):
    def __init__(
        self,
        base_indexer_addr: Addr,
        base_values_addr: Addr,
    ):
        super().__init__()
        self.generator = Model(
            base_indexer_addr=base_indexer_addr,
            base_values_addr=base_values_addr,
            int_regfile_size=384,
            fp_regfile_size=224,
            request_gen_latency=3,
            request_gen_bandwidth=4,
            request_buffer_size=32,
            send_bandwidth=2,
        )
        self._kernels = []

    @overrides(AbstractCore)
    def connect_dcache(self, port: Port) -> None:
        self.generator.port = port

    def add_kernel(self, kernel: SpatterKernel) -> None:
        self._kernels.append(kernel)

    def start_traffic(self) -> None:
        for kernel in self._kernels:
            print(f"Adding kernel: {kernel}")
            self.generator.addKernel(*kernel.cxx_call_args())
