from typing import TypeAlias, Tuple
import attr
import numpy as np
from matplotlib import pyplot as plt

dimension: TypeAlias = Tuple[float, float]


@attr.define
class Chip:
    chip_size: dimension = 26.0, 26.0
    border_spacing = dimension = (3.0, 3.0)
    comparment_grid: tuple[int, int] = (9, 9)
    comparment_spacing: dimension = (0.3, 0.3)
    compartment_size: dimension = 2, 2
    feature_grid: tuple[int, int] = (24, 24)
    feature_size: dimension = 0.15, 0.15
    feature_spacing: dimension = 0.015, 0.015
    grid: np.ndarray = attr.field()

    @grid.default
    def _grid(self):
        return np.zeros((*self.comparment_grid, *self.feature_grid))

    def get_compartment_position(self, xg: int, yg: int) -> dimension:
        """Returns the bottom-left of the comparment with the given coordinates"""
        x = (
            self.compartment_size[0] * xg
            + xg * self.comparment_spacing[0]
            + self.border_spacing[0]
        )
        y = (
            self.compartment_size[1] * yg
            + yg * self.comparment_spacing[1]
            + self.border_spacing[1]
        )
        return x, y

    def get_feature_position(self, xg, yg, x, y) -> dimension:
        """Returns the bottom-left of the feature with the given coordinates"""
        cp = self.get_compartment_position(xg, yg)
        fs = (self.feature_size[0] + self.feature_spacing[0]) * x, (
            self.feature_size[1] + self.feature_spacing[1]
        ) * y
        return (cp[0] + fs[0], cp[1] + fs[1])

    def get_feature_center_position(self, xg, yg, x, y) -> dimension:
        """Returns the center of the feature with the given coordinates"""
        fp = self.get_feature_position(xg, yg, x, y)
        return (fp[0]+self.feature_size[0]/2, fp[1]+self.feature_size[1]/2)

def draw_chip(chip: Chip):
    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"), figsize=(10, 10))
    ax.set_xlim(0, chip.chip_size[0])
    ax.set_ylim(0, chip.chip_size[1])

    for xg, yg in np.ndindex(chip.comparment_grid):
        x_pos, y_pos = chip.get_compartment_position(xg, yg)
        ax.add_patch(
            plt.Rectangle(
                (x_pos, y_pos), *chip.compartment_size, color="black", alpha=0.5
            )
        )

def draw_comparment(chip: Chip, xg: int, yg: int):
    fig, ax = plt.subplots(subplot_kw=dict(aspect="equal"), figsize=(10, 10))
    ax.set_xlim(0, chip.compartment_size[0])
    ax.set_ylim(0, chip.compartment_size[1])
    for x, y, in np.ndindex(chip.feature_grid):
        x_pos, y_pos = chip.get_feature_position(xg, yg, x, y)
        x_pos -= chip.border_spacing[0]
        y_pos -= chip.border_spacing[1]
        ax.add_patch(
            plt.Rectangle(
                (x_pos, y_pos), *chip.feature_size, color="black", alpha=0.5
            )
        )


if __name__ == "__main__":

    chip = Chip()
    print(chip.feature_grid[0] * (chip.feature_size[0] + chip.feature_spacing[0]))
    draw_chip(chip)
    draw_comparment(chip, 0, 0)
    plt.show()
