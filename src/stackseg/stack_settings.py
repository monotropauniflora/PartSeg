from typing import List

import numpy as np
from matplotlib import pyplot

from partseg.io_functions import save_stack_segmentation, load_stack_segmentation
from qt_import import QObject, pyqtSignal
from stackseg.stack_algorithm.segment import cut_with_mask, save_catted_list
from project_utils.image_operations import normalize_shape

default_colors = ['BlackRed', 'BlackGreen', 'BlackBlue', 'BlackMagenta']


class ImageSettings(QObject):
    """
    :type _image: np.ndarray
    """
    image_changed = pyqtSignal([np.ndarray], [int], [str])
    segmentation_changed = pyqtSignal(np.ndarray)

    def __init__(self):
        super(ImageSettings, self).__init__()
        self.open_directory = None
        self.save_directory = None
        self._image = None
        self._image_path = ""
        self.has_channels = False
        self.image_spacing = 70, 70, 210
        self._segmentation = None
        self.chosen_components_widget = None
        self.sizes = []
        self.colors = []
        self.chosen_colormap = pyplot.colormaps()

    @property
    def segmentation(self) -> np.ndarray:
        return self._segmentation

    @segmentation.setter
    def segmentation(self, val: np.ndarray):
        self._segmentation = val
        if val is not None:
            self.sizes = np.bincount(val.flat)
            self.segmentation_changed.emit(val)
        else:
            self.sizes = []

    def chosen_components(self) -> List[int]:
        if self.chosen_components_widget is not None:
            return sorted(self.chosen_components_widget.get_chosen())
        else:
            raise RuntimeError("chosen_components_widget do not idealized")

    def component_is_chosen(self, val: int) -> bool:
        if self.chosen_components_widget is not None:
            return self.chosen_components_widget.get_state(val)
        else:
            raise RuntimeError("chosen_components_widget do not idealized")

    def save_segmentation(self, file_path: str):
        save_stack_segmentation(file_path, self.segmentation, self.chosen_components(), self._image_path)

    def load_segmentation(self, file_path: str):
        self.segmentation, metadata = load_stack_segmentation(file_path)
        num = self.segmentation.max()
        self.chosen_components_widget.set_chose(range(1, num + 1), metadata["components"])

    def set_segmentation(self, segmentation, metadata):
        self.segmentation = segmentation
        num = self.segmentation.max()
        self.chosen_components_widget.set_chose(range(1, num + 1), metadata["components"])

    def save_result(self, dir_path: str):
        res_img = cut_with_mask(self.segmentation, self._image, only=self.chosen_components())
        res_mask = cut_with_mask(self.segmentation, self.segmentation, only=self.chosen_components())
        save_catted_list(res_img, dir_path, prefix="component")
        save_catted_list(res_mask, dir_path, prefix="component", suffix="_mask")

    @property
    def batch_directory(self):
        return self.open_directory

    @batch_directory.setter
    def batch_directory(self, val):
        self.open_directory = val

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        if isinstance(value, tuple):
            file_path = value[1]
            value = value[0]
        else:
            file_path = None
        value = np.squeeze(value)
        self._image = normalize_shape(value)

        if file_path is not None:
            self._image_path = file_path
            self.image_changed[str].emit(self._image_path)
        if self._image.shape[-1] < 10:
            self.has_channels = True
        else:
            self.has_channels = False

        for i in range (len(self.colors), self.channels):
            self.colors.append(default_colors[i % len(default_colors)])


        self.image_changed.emit(self._image)
        self.image_changed[int].emit(self.channels)

    @property
    def image_path(self):
        return self._image_path

    @image_path.setter
    def image_path(self, value):
        self._image_path = value
        self.image_changed[str].emmit(self._image_path)

    @property
    def channels(self):
        if self._image is None:
            return 0
        if len(self._image.shape) == 4:
            return self._image.shape[-1]
        else:
            return 1

    def get_chanel(self, chanel_num):
        if self.has_channels:
            return self._image[..., chanel_num]
        return self._image

    def get_information(self, *pos):
        return self._image[pos]
