import numpy as np

from src.augmentation.augmentation_config import AugmentationConfig
from src.augmentation.augmentation_pipeline import AugmentationPipeline


class TestAugmentationStress:
    @classmethod
    def setup_class(cls):
        cls.large_image = np.full((1024, 1024, 3), 128, dtype=np.uint8)

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

    def test_large_image_full_pipeline(self):
        result = self.pipeline.process(self.large_image, seed=42)
        assert len(result.image.shape) == 3
        assert result.image.shape[2] == 3
        assert result.image.dtype == np.uint8
        assert len(result.applied_transforms) >= 1

    def test_many_seeds_no_crash(self):
        for seed in range(100):
            result = self.pipeline.process(self.large_image, seed=seed)
            assert len(result.image.shape) == 3
            assert result.image.shape[2] == 3
            assert result.image.dtype == np.uint8

    def test_extreme_rotation_and_perspective(self):
        config = AugmentationConfig()
        config.disable_all()
        config.rotation["enabled"] = True
        config.rotation["probability"] = 1.0
        config.rotation["angle_range"] = [170, 170]
        config.perspective["enabled"] = True
        config.perspective["probability"] = 1.0
        config.perspective["strength"] = 0.7
        pipe = AugmentationPipeline(config)

        for seed in range(50):
            result = pipe.process(self.large_image, seed=seed)
            assert result.image.shape[0] > 0 and result.image.shape[1] > 0
            assert result.image.dtype == np.uint8

    def test_all_augmentations_extreme_params(self):
        config = AugmentationConfig()
        config.rotation["probability"] = 1.0
        config.rotation["angle_range"] = [180, 180]
        config.perspective["probability"] = 1.0
        config.perspective["strength"] = 0.8
        config.lighting["probability"] = 1.0
        config.lighting["brightness_range"] = [3.0, 3.0]
        config.lighting["gamma_range"] = [2.5, 2.5]
        config.lighting["exposure_range"] = [2.0, 2.0]
        config.contrast["probability"] = 1.0
        config.contrast["alpha_range"] = [3.0, 3.0]
        config.blur["probability"] = 1.0
        config.blur["gaussian_kernel_range"] = [11, 11]
        config.noise["probability"] = 1.0
        config.noise["gaussian_std_range"] = [50, 50]
        config.noise["salt_pepper_amount_range"] = [0.3, 0.3]
        config.color["probability"] = 1.0
        config.color["saturation_range"] = [3.0, 3.0]
        config.color["hue_range"] = [30, 30]
        pipe = AugmentationPipeline(config)

        for seed in range(30):
            result = pipe.process(self.large_image, seed=seed)
            assert len(result.image.shape) == 3
            assert result.image.shape[2] == 3
            assert result.image.dtype == np.uint8
            assert len(result.applied_transforms) >= 1
