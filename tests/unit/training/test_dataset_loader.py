import os
import tempfile
import pytest

from src.training.dataset_loader import DatasetLoader, DatasetInfo


class TestDatasetLoader:
    @pytest.fixture
    def yolo_dataset(self):
        with tempfile.TemporaryDirectory() as root:
            for split in ["train", "val"]:
                os.makedirs(os.path.join(root, split, "images"))
                os.makedirs(os.path.join(root, split, "labels"))
                with open(os.path.join(root, split, "images", "img001.jpg"), "w") as f:
                    f.write("fake image")
                with open(os.path.join(root, split, "labels", "img001.txt"), "w") as f:
                    f.write("0 0.5 0.5 0.4 0.6\n")
            yield root

    def test_load_yolo(self, yolo_dataset):
        loader = DatasetLoader()
        info = loader.load(yolo_dataset, format="yolo")
        assert info.format == "yolo"
        assert info.train_images == 1
        assert info.train_labels == 1
        assert info.val_images == 1
        assert info.val_labels == 1
        assert info.total_images == 2
        assert info.total_labels == 2

    def test_load_coco(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "coco.json"), "w") as f:
                f.write('{"categories": [{"id": 1, "name": "card"}], "images": [{"id": 1}], "annotations": [{"id": 1}]}')
            loader = DatasetLoader()
            info = loader.load(root, format="coco")
            assert info.format == "coco"
            assert info.num_classes == 1

    def test_load_custom(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "train", "images"))
            os.makedirs(os.path.join(root, "train", "labels"))
            with open(os.path.join(root, "train", "images", "test.jpg"), "w") as f:
                f.write("fake")
            with open(os.path.join(root, "train", "labels", "test.txt"), "w") as f:
                f.write("0 0.5 0.5 0.2 0.3\n")
            loader = DatasetLoader()
            info = loader.load(root, format="custom")
            assert info.total_images == 1

    def test_validate_clean(self, yolo_dataset):
        loader = DatasetLoader()
        info = loader.load(yolo_dataset)
        issues = loader.validate(info)
        assert len(issues) == 0

    def test_validate_empty(self):
        with tempfile.TemporaryDirectory() as root:
            loader = DatasetLoader()
            info = loader.load(root)
            issues = loader.validate(info)
            assert len(issues) > 0
            assert any("No images" in i for i in issues)

    def test_invalid_labels(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "train", "images"))
            os.makedirs(os.path.join(root, "train", "labels"))
            with open(os.path.join(root, "train", "images", "bad.jpg"), "w"):
                pass
            with open(os.path.join(root, "train", "labels", "bad.txt"), "w") as f:
                f.write("not valid yolo format\n")
            loader = DatasetLoader()
            info = loader.load(root, format="yolo")
            assert len(info.invalid_labels) > 0

    def test_dataset_info_to_dict(self):
        info = DatasetInfo(format="yolo", num_classes=1, total_images=10)
        d = info.to_dict()
        assert d["format"] == "yolo"
        assert d["total_images"] == 10
