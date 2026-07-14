from __future__ import annotations

import pytest

from src.training.yolo_config import YOLOModelConfig
from src.training.dataset_loader import DatasetInfo
from src.training.yolo_data_pipeline import YOLODataPipeline, YOLOBatchStats


class TestYOLODataPipeline:
    @pytest.fixture
    def model_config(self):
        return YOLOModelConfig(arch="n", input_size=640)

    @pytest.fixture
    def dataset_info(self):
        return DatasetInfo(
            format="yolo",
            num_classes=1,
            class_names={0: "business_card"},
            train_images=100,
            train_labels=90,
            val_images=20,
            val_labels=18,
            test_images=10,
            test_labels=10,
            total_images=130,
            total_labels=118,
            has_valid_labels=True,
        )

    def test_build_pipeline(self, model_config, dataset_info):
        pipeline = YOLODataPipeline(model_config)
        stats = pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root="/fake/root",
            batch_size=16,
            workers=4,
        )
        assert isinstance(stats, YOLOBatchStats)
        assert stats.batch_size == 16
        assert stats.image_size == 640
        assert stats.mosaic_active
        assert stats.mixup_active

    def test_build_pipeline_stats_total(self, model_config, dataset_info):
        pipeline = YOLODataPipeline(model_config)
        stats = pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root="/fake/root",
            batch_size=16,
            workers=4,
        )
        assert stats.total_samples == 130
        assert stats.num_batches == 8  # 130 // 16

    def test_build_pipeline_zero_samples(self, model_config):
        empty_info = DatasetInfo(format="yolo")
        pipeline = YOLODataPipeline(model_config)
        stats = pipeline.build_pipeline(
            dataset_info=empty_info,
            dataset_root="/fake/root",
            batch_size=16,
            workers=4,
        )
        assert stats.total_samples == 0
        assert stats.num_batches == 0

    def test_loaders_property(self, model_config, dataset_info):
        pipeline = YOLODataPipeline(model_config)
        pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root="/fake/root",
            batch_size=16,
        )
        assert pipeline.train_loader is not None
        assert pipeline.train_loader["batch_size"] == 16
        assert pipeline.train_loader["shuffle"]
        assert pipeline.val_loader is not None
        assert not pipeline.val_loader["shuffle"]
        assert pipeline.test_loader is not None

    def test_loaders_no_val(self, model_config):
        info = DatasetInfo(train_images=50, train_labels=45)
        pipeline = YOLODataPipeline(model_config)
        pipeline.build_pipeline(dataset_info=info, dataset_root="/fake", batch_size=8)
        assert pipeline.train_loader is not None
        assert pipeline.val_loader is None
        assert pipeline.test_loader is None

    def test_get_dataset_sizes(self, model_config, dataset_info):
        pipeline = YOLODataPipeline(model_config)
        pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root="/fake/root",
            batch_size=16,
        )
        sizes = pipeline.get_dataset_sizes()
        assert sizes["train"] == 100
        assert sizes["val"] == 20
        assert sizes["test"] == 10

    def test_get_augmentation_info(self, model_config, dataset_info):
        pipeline = YOLODataPipeline(model_config)
        pipeline.build_pipeline(
            dataset_info=dataset_info,
            dataset_root="/fake/root",
            batch_size=16,
        )
        aug = pipeline.get_augmentation_info()
        assert aug["mosaic"] == 1.0
        assert aug["mixup"] == 0.1
        assert aug["auto_augment"] == "randaugment"


class TestYOLOBatchStats:
    def test_defaults(self):
        stats = YOLOBatchStats()
        assert stats.batch_size == 0
        assert stats.num_batches == 0
        assert stats.total_samples == 0
        assert not stats.mosaic_active

    def test_to_dict(self):
        stats = YOLOBatchStats(
            batch_size=32,
            num_batches=10,
            total_samples=320,
            image_size=640,
            mosaic_active=True,
        )
        d = stats.to_dict()
        assert d["batch_size"] == 32
        assert d["num_batches"] == 10
        assert d["total_samples"] == 320
        assert d["mosaic_active"]
