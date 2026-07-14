import os
import tempfile
import pytest

from src.annotations.annotation_validator import AnnotationValidator


class TestAnnotationValidator:
    def make_label(self, lines):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        for line in lines:
            f.write(line + "\n")
        f.close()
        return f.name

    def test_valid_single_object(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
            assert result.total_objects == 1
            assert result.valid_objects == 1
            assert result.line_results[0].class_id == 0
            assert result.line_results[0].x_center == 0.5
        finally:
            os.unlink(path)

    def test_valid_multiple_objects(self):
        path = self.make_label([
            "0 0.5 0.5 0.3 0.4",
            "1 0.2 0.3 0.1 0.2",
            "2 0.8 0.7 0.15 0.25",
        ])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
            assert result.total_objects == 3
            assert result.valid_objects == 3
        finally:
            os.unlink(path)

    def test_empty_file(self):
        path = self.make_label([])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert result.is_empty
            assert "empty" in result.errors[0].lower()
        finally:
            os.unlink(path)

    def test_file_not_found(self):
        result = AnnotationValidator().validate_file("nonexistent.txt")
        assert not result.is_valid
        assert "not found" in result.errors[0]

    def test_not_a_txt_file(self):
        f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        f.close()
        try:
            result = AnnotationValidator().validate_file(f.name)
            assert not result.is_valid
            assert "Not a .txt file" in result.errors[0]
        finally:
            os.unlink(f.name)

    def test_invalid_class_id_string(self):
        path = self.make_label(["abc 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert "not an integer" in result.line_results[0].errors[0]
        finally:
            os.unlink(path)

    def test_invalid_x_center_string(self):
        path = self.make_label(["0 abc 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert "not a number" in result.line_results[0].errors[0]
        finally:
            os.unlink(path)

    def test_negative_class_id(self):
        path = self.make_label(["-1 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_class_id_too_large(self):
        path = self.make_label(["1000 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_allowed_classes_valid(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator(allowed_classes=[0, 1, 2]).validate_file(path)
            assert result.is_valid
        finally:
            os.unlink(path)

    def test_allowed_classes_invalid(self):
        path = self.make_label(["5 0.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator(allowed_classes=[0, 1, 2]).validate_file(path)
            assert not result.is_valid
            assert "not in allowed classes" in result.line_results[0].errors[0]
        finally:
            os.unlink(path)

    def test_x_center_out_of_bounds_negative(self):
        path = self.make_label(["0 -0.1 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_x_center_out_of_bounds_above(self):
        path = self.make_label(["0 1.5 0.5 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_y_center_out_of_bounds(self):
        path = self.make_label(["0 0.5 -0.2 0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_width_zero(self):
        path = self.make_label(["0 0.5 0.5 0.0 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert any("must be positive" in e for e in result.line_results[0].errors)
        finally:
            os.unlink(path)

    def test_width_negative(self):
        path = self.make_label(["0 0.5 0.5 -0.3 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_height_zero(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.0"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_width_exceeds_one(self):
        path = self.make_label(["0 0.5 0.5 1.2 0.4"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_too_few_values(self):
        path = self.make_label(["0 0.5 0.5 0.3"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert "Expected 5" in result.line_results[0].errors[0]
        finally:
            os.unlink(path)

    def test_too_many_values(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.4 0.6"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_blank_line_in_middle(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.4", "", "1 0.2 0.3 0.1 0.2"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
            assert result.total_objects == 2
            assert result.valid_objects == 2
        finally:
            os.unlink(path)

    def test_whitespace_line(self):
        path = self.make_label(["0 0.5 0.5 0.3 0.4", "   ", "1 0.2 0.3 0.1 0.2"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
            assert result.valid_objects == 2
            assert result.total_objects == 2
        finally:
            os.unlink(path)

    def test_mixed_valid_invalid(self):
        path = self.make_label([
            "0 0.5 0.5 0.3 0.4",
            "abc 0.5 0.5 0.3 0.4",
            "1 0.2 0.3 0.1 0.2",
        ])
        try:
            result = AnnotationValidator().validate_file(path)
            assert not result.is_valid
            assert result.total_objects == 2
            assert result.valid_objects == 2
        finally:
            os.unlink(path)

    def test_custom_thresholds(self):
        validator = AnnotationValidator(allowed_classes=[0, 1])
        path = self.make_label(["2 0.5 0.5 0.3 0.4"])
        try:
            result = validator.validate_file(path)
            assert not result.is_valid
        finally:
            os.unlink(path)

    def test_boundary_valid_coords(self):
        path = self.make_label(["0 0.0 0.0 0.001 0.001"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
        finally:
            os.unlink(path)

    def test_boundary_max_coords(self):
        path = self.make_label(["0 1.0 1.0 1.0 1.0"])
        try:
            result = AnnotationValidator().validate_file(path)
            assert result.is_valid
        finally:
            os.unlink(path)
