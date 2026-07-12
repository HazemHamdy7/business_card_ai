from src.core.version import get_description, get_full_version, get_version


class TestVersion:
    def test_get_version(self) -> None:
        assert get_version() == "0.1.0"

    def test_get_full_version(self) -> None:
        full = get_full_version()
        assert "Business Card AI" in full
        assert "0.1.0" in full

    def test_get_description(self) -> None:
        desc = get_description()
        assert "Business Card" in desc
