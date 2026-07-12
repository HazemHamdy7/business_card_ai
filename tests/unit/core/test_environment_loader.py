from pathlib import Path

from src.core.config import EnvironmentLoader


class TestEnvironmentLoader:
    def test_load_nonexistent_file(self) -> None:
        loader = EnvironmentLoader(Path("nonexistent.env"))
        data = loader.load()
        assert data == {}

    def test_load_env_file(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\nKEY2=value2\n", encoding="utf-8")
        loader = EnvironmentLoader(env_file)
        data = loader.load()
        assert data["KEY1"] == "value1"
        assert data["KEY2"] == "value2"

    def test_load_env_file_with_comments(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("# comment\nKEY=value\n", encoding="utf-8")
        loader = EnvironmentLoader(env_file)
        data = loader.load()
        assert "KEY" in data
        assert data["KEY"] == "value"

    def test_load_env_file_with_quotes(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text('KEY="quoted_value"\n', encoding="utf-8")
        loader = EnvironmentLoader(env_file)
        data = loader.load()
        assert data["KEY"] == "quoted_value"

    def test_get_variable(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("MY_VAR=hello\n", encoding="utf-8")
        loader = EnvironmentLoader(env_file)
        loader.load()
        assert loader.get("MY_VAR") == "hello"

    def test_get_default(self) -> None:
        loader = EnvironmentLoader(Path("nonexistent.env"))
        loader.load()
        assert loader.get("NONEXISTENT", "default") == "default"

    def test_variables_property(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("A=1\nB=2\n", encoding="utf-8")
        loader = EnvironmentLoader(env_file)
        loader.load()
        assert loader.variables == {"A": "1", "B": "2"}
