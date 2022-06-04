import time

import attr
import sys
import typing
from stage_model import XYZStage
from smaract import ctl


@attr.define
class SmarActXYZ(XYZStage):
    name: str = 'SmarAct XYZ'
    handle: int = attr.ib(init=False)
    channels: dict[str, int] = {"x": 1, "y": 2, "z": 0}

    def __attrs_post_init__(self):
        buffer = ctl.FindDevices()
        if len(buffer) == 0:
            raise IOError("MCS2 no devices found.")
        locators = buffer.split("\n")
        self.handle = ctl.Open(locators[0])

        for c, idx in self.channels.items():
            ctl.SetProperty_i32(self.handle, idx, ctl.Property.MAX_CL_FREQUENCY, 10000)
            ctl.SetProperty_i32(self.handle, idx, ctl.Property.HOLD_TIME, 50)
            move_mode = ctl.MoveMode.CL_ABSOLUTE
            ctl.SetProperty_i32(self.handle, idx, ctl.Property.MOVE_MODE, move_mode)
            ctl.SetProperty_i64(self.handle, idx, ctl.Property.MOVE_VELOCITY, 20_000_000_000)
            # Set move acceleration to 20 mm/s2.
            ctl.SetProperty_i64(self.handle, idx, ctl.Property.MOVE_ACCELERATION, 10000000000000)
            ctl.SetProperty_i32(self.handle, idx, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)

    def get_position(self) -> typing.Tuple[float, float, float]:
        pos = []
        for c in ['x', 'y', 'z']:
            position = ctl.GetProperty_i64(self.handle, self.channels[c], ctl.Property.POSITION)
            pos.append(position * 1e-9)
        return tuple(pos)

    def move_to(self, x, y, z):
        if x is not None:
            ctl.Move(self.handle, self.channels['x'], round(x/1e-9), 0)
        if y is not None:
            ctl.Move(self.handle, self.channels['y'], round(y/1e-9), 0)
        if y is not None:
            ctl.Move(self.handle, self.channels['z'], round(y/1e-9), 0)

    def is_moving(self) -> bool:
        state = ctl.GetProperty_i32(self.handle, self.channels['x'], ctl.Property.CHANNEL_STATE)
        x_moving = state & ctl.ChannelState.ACTIVELY_MOVING
        state = ctl.GetProperty_i32(self.handle, self.channels['y'], ctl.Property.CHANNEL_STATE)
        y_moving = state & ctl.ChannelState.ACTIVELY_MOVING
        state = ctl.GetProperty_i32(self.handle, self.channels['z'], ctl.Property.CHANNEL_STATE)
        z_moving = state & ctl.ChannelState.ACTIVELY_MOVING
        return any((bool(x_moving), bool(y_moving), bool(z_moving)))


    def parse_error(self, e: ctl.Error):
        return "MCS2 {}: {}, error: {} (0x{:04X}) in line: {}.".format(e.func, ctl.GetResultInfo(e.code),
                                                                       ctl.ErrorCode(e.code).name, e.code,
                                                                       sys.exc_info()[-1].tb_lineno
                                                                       )


