from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import cv2
import numpy as np


@dataclass
class DuplicateReport:
    sha256_duplicates: List[Tuple[str, str]] = field(default_factory=list)
    perceptual_duplicates: List[Tuple[str, str]] = field(default_factory=list)
    near_duplicates: List[Tuple[str, str, float]] = field(default_factory=list)
    total_exact_duplicate_pairs: int = 0
    total_perceptual_duplicate_pairs: int = 0
    total_near_duplicate_pairs: int = 0
    unique_images: int = 0
    total_images_checked: int = 0


class DuplicateDetector:
    def __init__(self, hash_size: int = 8, threshold: float = 0.1):
        self.hash_size = hash_size
        self.threshold = threshold

    def find_duplicates(self, image_dir: str) -> DuplicateReport:
        report = DuplicateReport()
        if not os.path.isdir(image_dir):
            return report

        image_paths = self._collect_images(image_dir)
        report.total_images_checked = len(image_paths)

        sha256_map: Dict[str, List[str]] = {}
        phash_map: Dict[str, List[str]] = {}

        for path in image_paths:
            sha = self._sha256(path)
            sha256_map.setdefault(sha, []).append(path)

            ph = self._phash(path)
            if ph is not None:
                phash_map.setdefault(ph, []).append(path)

        for sha, paths in sha256_map.items():
            if len(paths) > 1:
                for i in range(len(paths)):
                    for j in range(i + 1, len(paths)):
                        report.sha256_duplicates.append((paths[i], paths[j]))
        report.total_exact_duplicate_pairs = len(report.sha256_duplicates)

        for ph, paths in phash_map.items():
            if len(paths) > 1:
                for i in range(len(paths)):
                    for j in range(i + 1, len(paths)):
                        report.perceptual_duplicates.append((paths[i], paths[j]))
        report.total_perceptual_duplicate_pairs = len(report.perceptual_duplicates)

        checked: Set[str] = set()
        ph_list = [(ph, paths) for ph, paths in phash_map.items()]
        for i in range(len(ph_list)):
            for j in range(i + 1, len(ph_list)):
                ph1, paths1 = ph_list[i]
                ph2, paths2 = ph_list[j]
                distance = self._hamming_distance(ph1, ph2)
                similarity = 1.0 - (distance / (self.hash_size * self.hash_size))
                if similarity > (1.0 - self.threshold):
                    for p1 in paths1:
                        for p2 in paths2:
                            key = (p1, p2) if p1 < p2 else (p2, p1)
                            if key not in checked:
                                checked.add(key)
                                report.near_duplicates.append(
                                    (p1, p2, similarity)
                                )
        report.total_near_duplicate_pairs = len(report.near_duplicates)

        seen: Set[str] = set()
        for dup_list in [report.sha256_duplicates, report.perceptual_duplicates]:
            for a, b in dup_list:
                seen.add(a)
                seen.add(b)
        report.unique_images = len(image_paths) - len(seen)

        return report

    def _collect_images(self, image_dir: str) -> List[str]:
        allowed = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
        result = []
        for fname in sorted(os.listdir(image_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext in allowed:
                result.append(os.path.join(image_dir, fname))
        return result

    def _sha256(self, path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def _phash(self, path: str) -> Optional[str]:
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            small = cv2.resize(img, (self.hash_size + 1, self.hash_size))
            diff = small[:, 1:] > small[:, :-1]
            bits = diff.flatten()
            hex_digits = []
            for i in range(0, len(bits), 4):
                nibble = 0
                for j in range(4):
                    if i + j < len(bits) and bits[i + j]:
                        nibble |= 1 << (3 - j)
                hex_digits.append(f"{nibble:x}")
            return "".join(hex_digits)
        except Exception:
            return None

    def _hamming_distance(self, hash1: str, hash2: str) -> int:
        max_len = max(len(hash1), len(hash2))
        hash1 = hash1.zfill(max_len)
        hash2 = hash2.zfill(max_len)
        distance = 0
        for c1, c2 in zip(hash1, hash2):
            v1 = int(c1, 16)
            v2 = int(c2, 16)
            xor = v1 ^ v2
            distance += bin(xor).count("1")
        return distance
