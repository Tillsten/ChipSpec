from concurrent.futures import thread
from .spec_model import ISpectrometer, Spectrum
from attrs import define, field, Factory
import numpy as np
import seabreeze

import threading
#seabreeze.use('pyseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer


@define
class OceanOptics(ISpectrometer):
    device: Spectrometer = field(factory=lambda: Spectrometer(list_devices()[0]))
    thread: threading.Thread|None = None
    spec_storage: dict = field(factory=dict)
    wavelengths: np.ndarray = Factory(lambda self: self.device.wavelengths(), takes_self=True)
    _reading: bool = False

    def reader_thread(self, integration_time: float, n_samples: int):
        self._reading = True
        self.device.integration_time_micros(int(integration_time*1000))
        spec_list = []
        for i in range(n_samples):
            spec_list.append(self.device.intensities())
        self.spec_storage['values'] = np.array(spec_list).mean(axis=0)
        self._reading = False


    def start_reading(self, integration_time: float, n_samples: int):
        if self.is_reading():
            raise IOError('Already reading')
        self.spec_storage['integration_time'] = integration_time
        self.spec_storage['n_samples'] = n_samples
        self.thread = threading.Thread(target=self.reader_thread, args=(integration_time, n_samples))
        self.thread.start()

    def is_reading(self) -> bool:
        return self._reading

    def get_reading(self) -> Spectrum:

        spec = Spectrum(wavelengths=self.device.wavelengths(), **self.spec_storage)
        self.spec_storage = {}
        return spec


if __name__ == '__main__':
    import pyqtgraph as pg
    app = pg.mkQApp()
    pw = pg.PlotWidget()

    spec = OceanOptics()
    for i in range(5):
        spec.start_reading(100, 1)
        while r := spec.is_reading():
            print(r)
        specdata = spec.get_reading()
    pw.plot(specdata.wavelengths, specdata.values)
    pw.show()


    app.exec_()