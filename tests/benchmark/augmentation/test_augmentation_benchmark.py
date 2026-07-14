import time
import numpy as np

from src.augmentation.augmentation_config import AugmentationConfig
from src.augmentation.augmentation_pipeline import AugmentationPipeline


class TestAugmentationBenchmark:
    @classmethod
    def setup_class(cls):
        cls.image_100 = np.full((100, 100, 3), 128, dtype=np.uint8)
        cls.image_500 = np.full((500, 500, 3), 128, dtype=np.uint8)

        config = AugmentationConfig()
        for aug_key in ["rotation", "perspective", "lighting", "contrast",
                         "blur", "noise", "color"]:
            getattr(config, aug_key)["enabled"] = True
            getattr(config, aug_key)["probability"] = 1.0
        config.rotation["angle_range"] = [30, 30]
        config.perspective["strength"] = 0.3
        config.lighting["brightness_range"] = [1.5, 1.5]
        config.contrast["alpha_range"] = [1.5, 1.5]
        config.blur["gaussian_kernel_range"] = [5, 5]
        config.noise["gaussian_std_range"] = [10, 10]
        config.color["saturation_range"] = [1.5, 1.5]
        cls.pipeline = AugmentationPipeline(config)

    def test_full_pipeline_throughput_100x100(self):
        iterations = 50
        start = time.perf_counter()
        for i in range(iterations):
            self.pipeline.process(self.image_100, seed=i)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 5

    def test_full_pipeline_throughput_500x500(self):
        iterations = 20
        start = time.perf_counter()
        for i in range(iterations):
            self.pipeline.process(self.image_500, seed=i)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 1

    def test_single_augmentation_speed(self):
        config = AugmentationConfig()
        config.disable_all()
        config.rotation["enabled"] = True
        config.rotation["probability"] = 1.0
        config.rotation["angle_range"] = [45, 45]
        pipe = AugmentationPipeline(config)

        iterations = 200
        start = time.perf_counter()
        for i in range(iterations):
            pipe.process(self.image_100, seed=i)
        elapsed = time.perf_counter() - start
        ops_per_sec = iterations / elapsed
        assert ops_per_sec > 50
