from abc import ABC

from project_utils.image_operations import gaussian, RadiusType
from project_utils.segmentation.algorithm_describe_base import AlgorithmDescribeBase
from tiff_image import Image


def calculate_operation_radius(radius, spacing, gauss_type):
    if gauss_type == RadiusType.R2D:
        if len(spacing) == 3:
            spacing = spacing[1:]
    base = min(spacing)
    if base != max(spacing):
        ratio = [x / base for x in spacing]
        return [radius / r for r in ratio]
    return radius


class SegmentationAlgorithm(AlgorithmDescribeBase, ABC):
    def __init__(self):
        super().__init__()
        self.image: Image = None
        self.channel = None
        self.segmentation = None

    def _clean(self):
        self.image = None
        self.segmentation = None

    def calculation_run(self, report_fun):
        raise NotImplementedError()

    def get_info_text(self):
        raise NotImplementedError()

    def get_channel(self, channel_idx):
        return self.image.get_channel(channel_idx)

    def get_gauss(self, gauss_type, gauss_radius):
        if gauss_type == RadiusType.NO:
            return self.channel
        assert isinstance(gauss_type, RadiusType)
        gauss_radius = calculate_operation_radius(gauss_radius, self.image.spacing, gauss_type)
        layer = gauss_type == RadiusType.R2D
        return gaussian(self.channel, gauss_radius, layer=layer)

    def set_image(self, image):
        self.image = image

    def set_exclude_mask(self, exclude_mask):
        """For Stack Seg - designed for mask part of image - maybe use standardize it to mask"""
        pass

    def set_parameters(self, *args, **kwargs):
        raise NotImplementedError()
