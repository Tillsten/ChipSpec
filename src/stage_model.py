from typing import Protocol
import asyncio

import numpy as np


class XYZStage(Protocol):
    def move_to(self, x: float, y: float, z: float):
        ...

    def is_moving(self) -> bool:
        ...

    def get_position(self) -> tuple[float, float, float]:
        ...

    async def move_async(self, x: float, y: float, z: float) -> None:
        self.move_to(x, y, z)
        while self.is_moving():
            await asyncio.sleep(0.05)
