import typing
from abc import ABC
from enum import Enum
import numpy as np

from ..image_operations import gaussian, median
from ..algorithm_describe_base import AlgorithmDescribeBase, AlgorithmProperty, Register
from ..class_generator import enum_register


class GaussType(Enum):
    Layer = 1
    Stack = 2

    def __str__(self):
        return self.name.replace("_", " ")


try:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    reloading
except NameError:
    reloading = False  # means the module is being imported
    enum_register.register_class(GaussType)


class NoiseFilteringBase(AlgorithmDescribeBase, ABC):
    @classmethod
    def noise_remove(cls, chanel: np.ndarray, spacing: typing.Iterable[float], arguments: dict) -> np.ndarray:
        raise NotImplementedError()


class NoneNoiseFiltering(NoiseFilteringBase):
    @classmethod
    def get_name(cls):
        return "None"

    @classmethod
    def get_fields(cls):
        return []

    @classmethod
    def noise_remove(cls, chanel: np.ndarray, spacing: typing.Iterable[float], arguments: dict):
        return chanel


class GaussNoiseFiltering(NoiseFilteringBase):
    @classmethod
    def get_name(cls):
        return "Gauss"

    @classmethod
    def get_fields(cls):
        return [AlgorithmProperty("gauss_type", "Gauss type", GaussType.Layer),
                AlgorithmProperty("radius", "Gauss radius", 1.0, property_type=float)]

    @classmethod
    def noise_remove(cls, channel: np.ndarray, spacing: typing.Iterable[float], arguments: dict):
        gauss_radius = calculate_operation_radius(arguments["radius"], spacing, arguments["gauss_type"])
        layer = arguments["gauss_type"] == GaussType.Layer
        return gaussian(channel, gauss_radius, layer=layer)


def calculate_operation_radius(radius, spacing, gauss_type):
    if gauss_type == GaussType.Layer:
        if len(spacing) == 3:
            spacing = spacing[1:]
    base = min(spacing)
    if base != max(spacing):
        ratio = [x / base for x in spacing]
        return [radius / r for r in ratio]
    return radius


class MedianNoiseFiltering(NoiseFilteringBase):
    @classmethod
    def get_name(cls):
        return "Median"

    @classmethod
    def get_fields(cls):
        return [AlgorithmProperty("dimension_type", "Median type", GaussType.Layer),
                AlgorithmProperty("radius", "Median radius", 1.0, property_type=float)]

    @classmethod
    def noise_remove(cls, channel: np.ndarray, spacing: typing.Iterable[float], arguments: dict):
        gauss_radius = calculate_operation_radius(arguments["radius"], spacing, arguments["apply_type"])
        layer = arguments["apply_type"] == GaussType.Layer
        return median(channel, gauss_radius, layer=layer)


noise_removal_dict = Register(NoneNoiseFiltering, GaussNoiseFiltering, MedianNoiseFiltering,
                              class_methods=["noise_remove"])
