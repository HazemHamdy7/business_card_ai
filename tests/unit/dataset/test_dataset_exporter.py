import json
from pathlib import Path

from PIL import Image

from src.dataset.dataset_exporter import DatasetExporter


def _create_image(path: Path, size=(640, 480), color=(128, 128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color)
    img.save(path)


def _create_label(path: Path, lines: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.writelines(lines)


def _make_dataset(root: Path):
    for split in ["train", "val"]:
        for i in range(1, 3):
            stem = f"BCA001_00{i}_V1-0"
            _create_image(root / "raw" / split / "images" / f"{stem}.jpg", size=(640, 480))
            _create_label(root / "raw" / split / "labels" / f"{stem}.txt", ["0 0.5 0.5 0.4 0.5\n"])
    return root


class TestDatasetExporter:
    def test_export_yolo(self, tmp_path):
        root = _make_dataset(tmp_path / "dataset")
        output = tmp_path / "yolo_export"
        exporter = DatasetExporter(root)
        result = exporter.export_yolo(output, splits=["train"])
        assert result == output
        assert (output / "train" / "images").exists()
        assert (output / "train" / "labels").exists()
        image_files = list((output / "train" / "images").iterdir())
        label_files = list((output / "train" / "labels").iterdir())
        assert len(image_files) == 2
        assert len(label_files) == 2

    def test_export_yolo_multiple_splits(self, tmp_path):
        root = _make_dataset(tmp_path / "dataset")
        output = tmp_path / "yolo_export"
        exporter = DatasetExporter(root)
        exporter.export_yolo(output, splits=["train", "val"])
        assert (output / "train" / "images").exists()
        assert (output / "val" / "images").exists()

    def test_export_coco(self, tmp_path):
        root = _make_dataset(tmp_path / "dataset")
        output = tmp_path / "coco_export"
        exporter = DatasetExporter(root)
        result = exporter.export_coco(output, splits=["train"])
        assert result == output
        assert (output / "train" / "images").exists()
        json_path = output / "train_annotations.json"
        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)
        assert "images" in data
        assert "annotations" in data
        assert "categories" in data
        assert len(data["images"]) == 2
        assert len(data["annotations"]) == 2

    def test_export_coco_annotation_conversion(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "raw" / "train" / "images" / "BCA001_001_V1-0.jpg", size=(1000, 500))
        _create_label(root / "raw" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.4\n"])
        exporter = DatasetExporter(root)
        output = tmp_path / "coco_export"
        exporter.export_coco(output, splits=["train"])
        with open(output / "train_annotations.json") as f:
            data = json.load(f)
        ann = data["annotations"][0]
        img = data["images"][0]
        assert img["width"] == 1000
        assert img["height"] == 500
        assert ann["bbox"] == [300.0, 150.0, 400.0, 200.0]

    def test_export_split(self, tmp_path):
        root = _make_dataset(tmp_path / "dataset")
        output = tmp_path / "split_export"
        exporter = DatasetExporter(root)
        result = exporter.export_split("train", output)
        assert result == output / "train"
        assert (output / "train" / "images").exists()
        assert (output / "train" / "labels").exists()

    def test_export_empty_split(self, tmp_path):
        root = tmp_path / "dataset"
        root.mkdir()
        output = tmp_path / "empty_export"
        exporter = DatasetExporter(root)
        result = exporter.export_split("train", output)
        assert result == output / "train"
        assert (output / "train" / "images").exists() == False
        assert (output / "train" / "labels").exists() == False

    def test_export_coco_empty_split(self, tmp_path):
        root = tmp_path / "dataset"
        root.mkdir()
        output = tmp_path / "coco_empty"
        exporter = DatasetExporter(root)
        result = exporter.export_coco(output, splits=["train"])
        json_path = output / "train_annotations.json"
        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)
        assert data["images"] == []
        assert data["annotations"] == []

    def test_export_yolo_custom_source(self, tmp_path):
        root = tmp_path / "dataset"
        _create_image(root / "custom" / "train" / "images" / "BCA001_001_V1-0.jpg")
        _create_label(root / "custom" / "train" / "labels" / "BCA001_001_V1-0.txt", ["0 0.5 0.5 0.4 0.5\n"])
        output = tmp_path / "yolo_custom"
        exporter = DatasetExporter(root)
        exporter.export_yolo(output, splits=["train"], source="custom")
        assert (output / "train" / "images" / "BCA001_001_V1-0.jpg").exists()
