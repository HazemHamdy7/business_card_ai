import os
import tempfile
import pytest

from src.training.training_config import (
    TrainingConfig,
    OptimizerConfig,
    SchedulerConfig,
    AugmentationConfig,
)


class TestOptimizerConfig:
    def test_defaults(self):
        opt = OptimizerConfig()
        assert opt.name == "AdamW"
        assert opt.lr == 0.001

    def test_from_dict(self):
        opt = OptimizerConfig.from_dict({"name": "SGD", "lr": 0.01})
        assert opt.name == "SGD"
        assert opt.lr == 0.01

    def test_to_dict(self):
        opt = OptimizerConfig(lr=0.01)
        d = opt.to_dict()
        assert d["lr"] == 0.01


class TestSchedulerConfig:
    def test_defaults(self):
        sched = SchedulerConfig()
        assert sched.name == "CosineAnnealingLR"

    def test_from_dict(self):
        sched = SchedulerConfig.from_dict({"name": "StepLR", "step_size": 30})
        assert sched.name == "StepLR"


class TestAugmentationConfig:
    def test_defaults(self):
        aug = AugmentationConfig()
        assert aug.fliplr == 0.5

    def test_from_dict(self):
        aug = AugmentationConfig.from_dict({"mosaic": 0.5, "mixup": 0.2})
        assert aug.mosaic == 0.5
        assert aug.mixup == 0.2


class TestTrainingConfig:
    def test_defaults(self):
        config = TrainingConfig()
        assert config.batch_size == 16
        assert config.epochs == 100
        assert config.seed == 42
        assert config.device == "auto"
        assert config.dataset_format == "yolo"

    def test_to_dict(self):
        config = TrainingConfig(batch_size=32, epochs=50)
        d = config.to_dict()
        assert d["batch_size"] == 32
        assert d["epochs"] == 50

    def test_from_dict(self):
        config = TrainingConfig.from_dict({
            "batch_size": 64,
            "epochs": 200,
            "optimizer": {"name": "SGD", "lr": 0.01},
        })
        assert config.batch_size == 64
        assert config.epochs == 200
        assert config.optimizer.name == "SGD"

    def test_save_and_load(self):
        config = TrainingConfig(batch_size=8, seed=123)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            config.save(path)
            loaded = TrainingConfig.load(path)
            assert loaded.batch_size == 8
            assert loaded.seed == 123
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_from_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"batch_size": 4, "epochs": 10}')
            f.close()
        try:
            config = TrainingConfig.from_json(f.name)
            assert config.batch_size == 4
            assert config.epochs == 10
        finally:
            os.unlink(f.name)

    def test_optimizer_config_in_config(self):
        config = TrainingConfig()
        assert isinstance(config.optimizer, OptimizerConfig)
        assert isinstance(config.scheduler, SchedulerConfig)
        assert isinstance(config.augmentation, AugmentationConfig)
