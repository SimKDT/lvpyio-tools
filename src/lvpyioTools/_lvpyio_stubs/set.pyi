from typing import Protocol
from lvpyio.types.buffer import Buffer
from lvpyio.types.scale import Scales

class Set(Protocol):
    """Type stub for lvpyio.io.set.Set"""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> Buffer: ...
    def close(self) -> None: ...