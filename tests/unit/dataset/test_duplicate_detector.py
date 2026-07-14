import os
import tempfile

import cv2
import numpy as np
import pytest

from src.dataset.duplicate_detector import DuplicateDetector


class TestDuplicateDetector:
    def make_image(self, directory, name="test.jpg", pixels=None, w=100, h=100):
        path = os.path.join(directory, name)
        if pixels is not None:
            img = pixels
        else:
            img = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
        cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        return path

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_images_checked == 0
            assert report.total_exact_duplicate_pairs == 0

    def test_no_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_image(tmp, "img1.jpg")
            self.make_image(tmp, "img2.jpg")
            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_images_checked == 2
            assert report.total_exact_duplicate_pairs == 0

    def test_sha256_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            pixels = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            self.make_image(tmp, "img1.jpg", pixels=pixels)
            self.make_image(tmp, "img2.jpg", pixels=pixels)

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_exact_duplicate_pairs >= 1

    def test_perceptual_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            pixels = np.full((100, 100, 3), 128, dtype=np.uint8)
            self.make_image(tmp, "img1.jpg", pixels=pixels)
            self.make_image(tmp, "img2.jpg", pixels=pixels)

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_perceptual_duplicate_pairs >= 1

    def test_non_image_file_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_image(tmp, "img1.jpg")
            with open(os.path.join(tmp, "notes.txt"), "w") as f:
                f.write("not an image")

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_images_checked == 1

    def test_sha256_different_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.make_image(tmp, "img1.jpg")
            self.make_image(tmp, "img2.jpg")

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_exact_duplicate_pairs == 0

    def test_phash_none_on_corrupted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.jpg")
            with open(path, "w") as f:
                f.write("not an image")

            d = DuplicateDetector()
            report = d.find_duplicates(tmp)
            assert report.total_perceptual_duplicate_pairs == 0

    def test_hamming_distance(self):
        d = DuplicateDetector()
        assert d._hamming_distance("abc", "abc") == 0
        assert d._hamming_distance("0000", "ffff") > 0
