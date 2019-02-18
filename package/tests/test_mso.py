import itertools

import pytest
from PartSeg.utils.distance_in_structure.euclidean_cython import calculate_euclidean

from PartSeg.utils.multiscale_opening import PyMSO, calculate_mu, MuType
import numpy as np

from PartSeg.utils.segmentation.sprawl import NeighType, calculate_distances_array


class TestMu:
    def test_base_mu(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        res = calculate_mu(image, 2, 8, MuType.base_mu)
        assert np.all(res == (image > 0).astype(np.float64))
        res = calculate_mu(image, 5, 15, MuType.base_mu)
        assert np.all(res == (image > 0).astype(np.float64) * 0.5)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 5, 15, MuType.base_mu)
        assert np.all(res == ((image > 0).astype(np.float64) + (image > 15).astype(np.float64)) * 0.5)

    def test_base_mu_masked(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        res = calculate_mu(image, 2, 8, MuType.base_mu, image > 0)
        assert np.all(res == (image > 0).astype(np.float64))
        res = calculate_mu(image, 5, 15, MuType.base_mu, image > 0)
        assert np.all(res == (image > 0).astype(np.float64) * 0.5)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 5, 15, MuType.base_mu, image > 0)
        assert np.all(res == ((image > 0).astype(np.float64) + (image > 15).astype(np.float64)) * 0.5)

    def test_reversed_base_mu(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        res = calculate_mu(image, 8, 2, MuType.base_mu)
        assert np.all(res == (image == 0).astype(np.float64))
        res = calculate_mu(image, 15, 5, MuType.base_mu)
        assert np.all(res == ((20 - image)/20).astype(np.float64))
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 15, 5, MuType.base_mu)
        assert np.all(res == (20 - image)/20)

    def test_reversed_base_mu_masked(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        mask = image > 0
        res = calculate_mu(image, 8, 2, MuType.base_mu, mask)
        assert np.all(res == np.zeros(image.shape, dtype=np.float64))
        res = calculate_mu(image, 15, 5, MuType.base_mu, mask)
        assert np.all(res == mask * 0.5)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 15, 5, MuType.base_mu, mask)
        assert np.all(res == (mask * (image < 20)) * 0.5)

    def test_reflection_mu(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        res = calculate_mu(image, 2, 8, MuType.reflection_mu)
        assert np.all(res == np.ones(image.shape, dtype=np.float64))
        res = calculate_mu(image, 5, 15, MuType.reflection_mu)
        assert np.all(res == (20 - image) / 20)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 5, 15, MuType.reflection_mu)
        assert np.all(res == np.ones(image.shape, dtype=np.float64) - (image == 10) * 0.5)

    def test_reflection_mu_masked(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        mask = image > 0
        res = calculate_mu(image, 2, 8, MuType.reflection_mu, mask)
        assert np.all(res == mask * 1.0)
        res = calculate_mu(image, 5, 15, MuType.reflection_mu, mask)
        assert np.all(res == ((20 - image) / 20) * mask)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 5, 15, MuType.reflection_mu, mask)
        assert np.all(res == (np.ones(image.shape, dtype=np.float64) - (image == 10) * 0.5) * mask)

    def test_reversed_reflection_mu(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        res = calculate_mu(image, 8, 2, MuType.reflection_mu)
        assert np.all(res == np.ones(image.shape, dtype=np.float64))
        res = calculate_mu(image, 15, 5, MuType.reflection_mu)
        assert np.all(res == (20 - image) / 20)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 15, 5, MuType.reflection_mu)
        assert np.all(res == np.ones(image.shape, dtype=np.float64) - (image == 10) * 0.5)

    def test_reversed_reflection_mu_masked(self):
        image = np.zeros((10, 10, 10), dtype=np.uint8)
        image[2:8, 2:8, 2:8] = 10
        mask = image > 0
        res = calculate_mu(image, 8, 2, MuType.reflection_mu, mask)
        assert np.all(res == mask * 1.0)
        res = calculate_mu(image, 15, 5, MuType.reflection_mu, mask)
        assert np.all(res == ((20 - image) / 20) * mask)
        image[4:6, 4:6, 4:6] = 20
        res = calculate_mu(image, 15, 5, MuType.reflection_mu, mask)
        assert np.all(res == (np.ones(image.shape, dtype=np.float64) - (image == 10) * 0.5) * mask)

    def test_two_object_mu(self):
        # TODO
        image = np.zeros((10, 10, 10), dtype=np.uint8)


def test_mso_construct():
    data = PyMSO()


class TestOptimumErosionCalculate:
    def test_two_components(self):
        components = np.zeros((10, 10, 20), dtype=np.uint8)
        components[4:6, 4:6, 4:6] = 1
        components[4:6, 4:6, 14:16] = 2
        sprawl_area = np.zeros(components.shape, dtype=np.uint8)
        sprawl_area[2:8, 2:8, 2:18] = True
        sprawl_area[components > 0] = False
        fdt = np.zeros(components.shape, dtype=np.float64)
        mso = PyMSO()
        neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
        mso.set_neighbourhood(neigh, dist)
        mso.set_components(components)
        res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
        assert np.all(res == components)

        fdt[:] = 2
        fdt[:, :, 10] = 1
        components2 = np.zeros(components.shape, dtype=np.uint8)
        components2[2:8, 2:8, 2:10] = 1
        components2[2:8, 2:8, 11:18] = 2
        res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
        assert np.all(res == components2)
        fdt[5, 5, 10] = 2
        res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
        assert np.all(res == components)

    def test_chain_component_base(self):
        for i in range(2, 10):
            components = np.zeros((4, 5, i * 5), dtype=np.uint8)
            for j in range(i):
                components[2, 2, 5 * j + 2] = j+1
            fdt = np.ones(components.shape, dtype=np.float64) * 2
            for j in range(i-1):
                fdt[:, :, j*5+4] = 1
            sprawl_area = np.ones(components.shape, dtype=np.uint8)
            sprawl_area[components > 0] = False
            components2 = np.zeros(components.shape, dtype=np.uint8)
            for j in range(i):
                components2[:, :, (j * 5):(j*5)+4] = j+1
            components2[:, :, -1] = i
            neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
            mso = PyMSO()
            mso.set_neighbourhood(neigh, dist)
            mso.set_components(components)
            res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
            assert np.all(res == components2)

    def test_chain_component(self):
        for i in range(3, 10):
            components = np.zeros((10, 10, i * 10), dtype=np.uint8)
            for j in range(i):
                components[4:6, 4:6, (10*j + 4):(10 * j + 6)] = j+1
            fdt = np.ones(components.shape, dtype=np.float64) * 2
            for j in range(i-1):
                fdt[:, :, (j+1) * 10] = 1
            sprawl_area = np.zeros(components.shape, dtype=np.uint8)
            sprawl_area[2:8, 2:8, 2:(10 * i) - 2] = True
            sprawl_area[components > 0] = False
            components2 = np.zeros(components.shape, dtype=np.uint8)
            for j in range(i):
                components2[2:8, 2:8, (j * 10 + 1):(j+1)*10] = j+1
            components2[:, :, :2] = 0
            components2[:, :, -2:] = 0
            neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
            mso = PyMSO()
            mso.set_neighbourhood(neigh, dist)
            mso.set_components(components)
            res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
            assert np.all(res == components2)

    def test_bridges(self):
        components = np.zeros((10, 20, 30), dtype=np.uint8)
        components[4:6, 4:6, 4:6] = 1
        components[4:6, 4:6, 24:26] = 2
        components[4:6, 14:16, 14:16] = 3
        sprawl_area = np.zeros(components.shape, dtype=np.uint8)
        sprawl_area[2:9, 2:10, 2:28] = True
        sprawl_area[2:9, 10:18, 11:20] = True
        sprawl_area[components > 0] = False
        fdt = np.ones(components.shape, dtype=np.float64) * 2
        fdt[:, 10, :] = 1
        fdt[:, :, 10] = 1
        fdt[:, :, 20] = 1

        comp = np.copy(components)
        comp[2:9, 2:10, 2:10] = 1
        comp[2:9, 2:10, 21:28] = 2
        comp[2:9, 11:18, 11:20] = 3
        neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
        mso = PyMSO()
        mso.set_neighbourhood(neigh, dist)
        mso.set_components(components)
        res = mso.optimum_erosion_calculate(fdt, components, sprawl_area)
        assert np.all(res == comp)
        fdt2 = np.copy(fdt)
        fdt2[5, 5, 10] = 2
        comp2 = np.copy(comp)
        comp2[5, 5, 10] = 1
        comp2[2:9, 2:10, 11:20] = 1
        res = mso.optimum_erosion_calculate(fdt2, components, sprawl_area)
        assert np.all(res == comp2)
        fdt2 = np.copy(fdt)
        fdt2[5, 5, 20] = 2
        comp2 = np.copy(comp)
        comp2[5, 5, 20] = 2
        comp2[2:9, 2:10, 11:20] = 2
        res = mso.optimum_erosion_calculate(fdt2, components, sprawl_area)
        assert np.all(res == comp2)
        fdt2 = np.copy(fdt)
        fdt2[5, 10, 15] = 2
        comp2 = np.copy(comp)
        comp2[5, 10, 15] = 3
        comp2[2:9, 2:10, 11:20] = 3
        res = mso.optimum_erosion_calculate(fdt2, components, sprawl_area)
        assert np.all(res == comp2)


class TestFDT:
    def test_fdt_base(self):
        mso = PyMSO()
        neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
        components = np.zeros((10, 10, 10), dtype=np.uint8)
        components[3:7, 3:7, 3:7] = 1
        mso.set_neighbourhood(neigh, dist)
        mso.set_components(components)
        mso.set_mu_array(np.ones(components.shape))
        res = mso.calculate_FDT()
        arr = calculate_euclidean((components == 0).astype(np.uint8), components, neigh, dist)
        assert np.all(res == arr)
        mso.set_mu_array(np.ones(components.shape) * 0.5)
        res = mso.calculate_FDT()
        assert np.all(res == arr*0.5)
        mu = np.ones(components.shape) * 0.5
        mu[components > 0] = 1
        mso.set_mu_array(mu)
        arr *= 0.5
        arr[arr > 0] += 0.25
        arr[3:7, (0, 1, 2, 0, 1, 2, 9, 8, 7, 9, 8, 7), (0, 1, 2, 9 ,8 ,7 , 0, 1, 2, 9, 8, 7)] += np.sqrt(2)/4 - 0.25
        for i in range(3):
            lb = i
            ub = 9-i
            arr[lb, lb+1:ub, (lb, ub)] += np.sqrt(2)/4 - 0.25
            arr[lb, (lb, ub), lb+1:ub] += np.sqrt(2) / 4 - 0.25
            arr[ub, lb + 1:ub, (lb, ub)] += np.sqrt(2) / 4 - 0.25
            arr[ub, (lb, ub), lb + 1:ub] += np.sqrt(2) / 4 - 0.25
            for el in itertools.product([lb, ub], repeat=3):
                arr[el]+= np.sqrt(3) / 4 - 0.25
        for z, (y,x) in itertools.product([2, 7], itertools.product([0, 9], repeat=2)):
            arr[z, y, x] += np.sqrt(2) / 4 - 0.25
        for z, (y,x) in itertools.product([2, 7], itertools.product([1, 8], repeat=2)):
            arr[z, y, x] += np.sqrt(2) / 4 - 0.25
        for z, (y,x) in itertools.product([1, 8], itertools.product([0, 9], repeat=2)):
            arr[z, y, x] += np.sqrt(2) / 4 - 0.25
        res2 = mso.calculate_FDT()
        assert np.allclose(res2, arr)

    def test_fdt_simple(self):
        mso = PyMSO()
        neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
        components = np.zeros((3, 3, 3), dtype=np.uint8)
        components[1, 1, 1] = 1
        mso.set_neighbourhood(neigh, dist)
        mso.set_components(components)
        mso.set_mu_array(np.ones(components.shape))
        arr = np.zeros(components.shape)
        arr[(0, 0, 0, 0, 2, 2, 2, 2), (0, 0, 2, 2, 0, 0, 2, 2), (0, 2, 0, 2, 0, 2, 0, 2)] = np.sqrt(3)
        arr[(0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2), (0, 1, 1, 2, 0, 0, 2, 2, 0, 1, 1, 2),
            (1, 0, 2, 1, 0, 2, 0, 2, 1, 0, 2, 1)] = np.sqrt(2)
        arr[(0, 1, 1, 1, 1, 2), (1, 0, 1, 1, 2, 1), (1, 1, 0, 2, 1, 1)] = 1
        res = mso.calculate_FDT()
        assert np.all(res == arr)


class TestExceptions:
    def test_fdt(self):
        mso = PyMSO()
        neigh, dist = calculate_distances_array((1, 1, 1), NeighType.vertex)
        components = np.zeros((10, 10, 10), dtype=np.uint8)
        components[3:7, 3:7, 3:7] = 1
        mso.set_neighbourhood(neigh, dist)
        with pytest.raises(RuntimeError):
            mso.calculate_FDT()
        mso.set_components(components)
        with pytest.raises(RuntimeError):
            mso.calculate_FDT()


