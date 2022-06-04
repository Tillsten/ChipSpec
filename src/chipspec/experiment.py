import h5py
import pathlib

from attr import define, field

from .chip_model import ChipModel
from .spec_model import SpecModel
from .stage_model import StageModel

from typing import Protocol

class Plan(Protocol):
    def init(self):
        pass

    def run_step():
        pass

    def stop(self):
        pass

@define
class PosPlan:
    spec: SpecModel
    stage: StageModel
    pos_list: list

    



class ChipPlan:
    chip: ChipModel
    spec: SpecModel
    stage: StageModel
