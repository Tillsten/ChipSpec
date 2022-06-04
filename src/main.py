from os import abort
from attr import define, field

import qtpy.QtCore as qtc
import qtpy.QtWidgets as qtw
import qtpy.QtGui as qtg

import pyqtgraph as pg
import pyqtgraph.parametertree as pt
import pyqtgraph.parametertree.parameterTypes as ptypes

from pathlib import Path
import h5py as h5
import numpy as np


linear_params = {'name': 'In', 'type': 'group', 'children': [
    ]   }


import sys

from chipspec.spec_model import ISpectrometer
from chipspec.stage_model import XYZStage

@define
class Plan:
    fname: Path
    spec: ISpectrometer
    stage: XYZStage
    pos_list: list
    spectra: dict = field(factory=dict)
    do_abort: bool = False

    def plan(self):
        with h5.File(self.fname, 'w') as f:
            f.create_dataset('pos_list', data=self.pos_list)
            f.create_dataset('wavelengths', data=self.spec.wavelengths)

        for idx, pos in enumerate(self.pos_list):
            print(pos)
            self.stage.move_to(*pos)
            while self.stage.is_moving():
                yield "Moving Stage", self.stage.get_position()

            self.spec.start_reading(100, 2)
            while self.spec.is_reading():
                yield "Reading Spectrometer", None

            spec = self.spec.get_reading()
            yield "Spectrum", spec
            self.spectra[pos] = spec
            with h5.File(self.fname, 'w') as f:
                ds = f.create_dataset(str(idx), data=spec.values)
                ds.attrs['pos'] = pos
            if self.do_abort:
                break
        print('done')

def start_plan(planiter, pw):
    i = next(planiter)
    if i[0] == 'Moving Stage':
        new_status = 'Moving ' + str(i[1])
    elif i[0] == 'Reading Spectrometer':
        new_status = "Reading"
    elif i[0] == 'Spectrum':
        pw.plot(i[1].wavelengths, i[1].values)
        pass

def main():
    #from chipspec.smaract_stage import SmartActStage
    from chipspec.stage_model import SimStage
    from chipspec.spec_ocean_optics import OceanOptics
    app = qtw.QApplication([])

    x_val = np.linspace(-3, 3, 100)
    pos_list = [(0, 0, i) for i in x_val]
    pw = pg.PlotWidget()
    plan = Plan(spec=OceanOptics(), stage=SimStage(), pos_list=pos_list, fname=Path('test.h5'))
    pw.show()
    timer = qtc.QTimer()
    planiter = plan.plan()

    timer.timeout.connect(lambda: start_plan(planiter, pw))
    timer.start(30)
    app.exec_()





if __name__ == '__main__':

    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        print(traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)
    sys.excepthook = exception_hook
    main()