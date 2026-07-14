from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LineValidationResult:
    line_number: int
    raw: str
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    class_id: Optional[int] = None
    x_center: Optional[float] = None
    y_center: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


@dataclass
class AnnotationValidationResult:
    file_path: str
    is_valid: bool = False
    line_results: List[LineValidationResult] = field(default_factory=list)
    total_objects: int = 0
    valid_objects: int = 0
    errors: List[str] = field(default_factory=list)
    is_empty: bool = False


class AnnotationValidator:
    MIN_CLASS_ID = 0
    MAX_CLASS_ID = 999
    COORD_MIN = 0.0
    COORD_MAX = 1.0

    def __init__(self, allowed_classes: Optional[List[int]] = None):
        self.allowed_classes = allowed_classes

    def validate_file(self, label_path: str) -> AnnotationValidationResult:
        result = AnnotationValidationResult(file_path=label_path)

        if not os.path.exists(label_path):
            result.is_valid = False
            result.errors.append(f"File not found: {label_path}")
            return result

        if not label_path.lower().endswith(".txt"):
            result.is_valid = False
            result.errors.append("Not a .txt file")
            return result

        try:
            with open(label_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Failed to read file: {e}")
            return result

        parsed_lines = []
        for i, raw in enumerate(lines, start=1):
            line_result = self._validate_line(raw, i)
            if line_result.raw.strip() or not line_result.is_valid:
                parsed_lines.append(line_result)
            if line_result.is_valid and line_result.class_id is not None:
                result.valid_objects += 1

        result.line_results = parsed_lines
        result.total_objects = result.valid_objects

        has_content_lines = any(l.raw.strip() for l in parsed_lines if l.raw.strip())
        has_errors = any(l.errors for l in parsed_lines)
        result.is_empty = not has_content_lines and not has_errors

        if result.is_empty:
            result.errors.append("Label file is empty")
            result.is_valid = False
            return result

        invalid_count = sum(1 for l in parsed_lines if not l.is_valid)
        if invalid_count > 0:
            result.is_valid = False
            result.errors.append(f"{invalid_count} line(s) have errors")
        elif result.total_objects > 0:
            result.is_valid = True

        return result

    def _validate_line(self, raw: str, line_number: int) -> LineValidationResult:
        stripped = raw.strip()
        result = LineValidationResult(line_number=line_number, raw=raw.rstrip("\n"))

        if not stripped:
            result.is_valid = True
            return result

        parts = stripped.split()
        if len(parts) != 5:
            result.is_valid = False
            result.errors.append(
                f"Expected 5 values, got {len(parts)}: {' '.join(parts)}"
            )
            return result

        class_str, x_str, y_str, w_str, h_str = parts

        class_id = self._parse_int(class_str, "class_id", line_number, result)
        x_center = self._parse_float(x_str, "x_center", line_number, result)
        y_center = self._parse_float(y_str, "y_center", line_number, result)
        width = self._parse_float(w_str, "width", line_number, result)
        height = self._parse_float(h_str, "height", line_number, result)

        if class_id is not None:
            if class_id < self.MIN_CLASS_ID:
                result.errors.append(
                    f"class_id {class_id} < {self.MIN_CLASS_ID} (line {line_number})"
                )
            elif class_id > self.MAX_CLASS_ID:
                result.errors.append(
                    f"class_id {class_id} > {self.MAX_CLASS_ID} (line {line_number})"
                )
            if self.allowed_classes is not None and class_id not in self.allowed_classes:
                result.errors.append(
                    f"class_id {class_id} not in allowed classes {self.allowed_classes} (line {line_number})"
                )

        if x_center is not None:
            if not self.COORD_MIN <= x_center <= self.COORD_MAX:
                result.errors.append(
                    f"x_center {x_center} out of range [{self.COORD_MIN}, {self.COORD_MAX}] (line {line_number})"
                )

        if y_center is not None:
            if not self.COORD_MIN <= y_center <= self.COORD_MAX:
                result.errors.append(
                    f"y_center {y_center} out of range [{self.COORD_MIN}, {self.COORD_MAX}] (line {line_number})"
                )

        if width is not None:
            if width <= 0:
                result.errors.append(
                    f"width {width} must be positive (line {line_number})"
                )
            elif not self.COORD_MIN < width <= self.COORD_MAX:
                result.errors.append(
                    f"width {width} out of range (0, {self.COORD_MAX}] (line {line_number})"
                )

        if height is not None:
            if height <= 0:
                result.errors.append(
                    f"height {height} must be positive (line {line_number})"
                )
            elif not self.COORD_MIN < height <= self.COORD_MAX:
                result.errors.append(
                    f"height {height} out of range (0, {self.COORD_MAX}] (line {line_number})"
                )

        if class_id is not None:
            result.class_id = class_id
        if x_center is not None:
            result.x_center = x_center
        if y_center is not None:
            result.y_center = y_center
        if width is not None:
            result.width = width
        if height is not None:
            result.height = height

        if not result.errors:
            result.is_valid = True

        return result

    def _parse_int(self, s: str, field_name: str, line: int, result: LineValidationResult) -> Optional[int]:
        try:
            return int(s)
        except ValueError:
            result.errors.append(f"Invalid {field_name} '{s}': not an integer (line {line})")
            return None

    def _parse_float(self, s: str, field_name: str, line: int, result: LineValidationResult) -> Optional[float]:
        try:
            return float(s)
        except ValueError:
            result.errors.append(f"Invalid {field_name} '{s}': not a number (line {line})")
            return None
