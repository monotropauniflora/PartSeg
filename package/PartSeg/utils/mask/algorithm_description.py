from ..segmentation.segmentation_algorithm import final_algorithm_list
from ..segmentation.algorithm_describe_base import Register

mask_algorithm_dict = Register()
for el in final_algorithm_list:
    mask_algorithm_dict.register(el)
