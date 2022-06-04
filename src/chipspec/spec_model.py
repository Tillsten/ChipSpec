from attrs import define, field
from typing import Protocol
from datetime import datetime

import numpy as np
import asyncio

@define
class Spectrum:
    wavelengths: np.ndarray = field()
    values: np.ndarray = field()
    integration_time: float = field()
    n_samples: int = field()
    record_time: datetime = field(factory=datetime.now)


class ISpectrometer(Protocol):
    wavelengths: np.ndarray = field()
    
    def start_reading(self, integration_time: float, n_samples: int):
        ...

    def is_reading(self) -> bool:
        ...

    def get_reading(self) -> Spectrum:
        ...

    async def read_async(self, integration_time: float, n_samples: int) -> Spectrum:
        self.start_reading(integration_time, n_samples)
        while self.is_reading():
            await asyncio.sleep(0.05)
        return self.get_reading()

