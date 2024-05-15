from typing import List

from m5.objects import SpatterKernelType


class SpatterKernel:
    def __init__(
        self,
        kernel_id: int,
        kernel_delta: int,
        kernel_count: int,
        kernel_type: SpatterKernelType,
        kernel_trace: List[int],
    ):
        self._id = kernel_id
        self._delta = kernel_delta
        self._count = kernel_count
        self._type = kernel_type
        self._trace = kernel_trace

    def cxx_call_args(self):
        return [
            self._id,
            self._delta,
            self._count,
            self._type.getValue(),
            self._trace,
        ]

    def __str__(self):
        return (
            f"SpatterKernel(id={self._id}, delta={self._delta}, "
            f"count={self._count}, type={self._type}, "
            f"trace[:8]={[index for index in self._trace[:8]]}), "
        )
