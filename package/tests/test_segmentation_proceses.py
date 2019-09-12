import os.path
import pytest

from PartSegImage import ImageReader
from PartSegCore.analysis.algorithm_description import analysis_algorithm_dict
from PartSegCore.algorithm_describe_base import SegmentationProfile
from PartSegCore.analysis.load_functions import UpdateLoadedMetadataAnalysis
from PartSegCore.json_hooks import check_loaded_dict
from PartSegCore.segmentation.algorithm_base import SegmentationAlgorithm

from help_fun import get_test_dir


def empty(_a, _b):
    pass


class TestSegmentation:
    def test_profile_execute(self):
        profile_path = os.path.join(get_test_dir(), "segment_profile_test.json")
        # noinspection PyBroadException
        try:
            data = UpdateLoadedMetadataAnalysis.load_json_data(profile_path)
            assert check_loaded_dict(data)
        except Exception:
            pytest.fail("Fail in loading profile")
            return
        image = ImageReader.read_image(
            os.path.join(get_test_dir(), "stack1_components", "stack1_component5.tif"),
            os.path.join(get_test_dir(), "stack1_components", "stack1_component5_mask.tif")
        )

        val: SegmentationProfile
        for val in data.values():
            algorithm: SegmentationAlgorithm = analysis_algorithm_dict[val.algorithm]()
            algorithm.set_image(image)
            algorithm.set_mask(image.mask.squeeze())
            algorithm.set_parameters(**val.values)
            result = algorithm.calculation_run(empty)
            assert result.segmentation.max() == 2
