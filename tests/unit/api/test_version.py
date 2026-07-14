from src.api.version import VERSION, API_VERSION, TITLE, DESCRIPTION, get_version_info


class TestVersion:
    def test_constants(self):
        assert isinstance(VERSION, str)
        assert len(VERSION) > 0
        assert isinstance(API_VERSION, str)
        assert len(API_VERSION) > 0
        assert isinstance(TITLE, str)
        assert len(TITLE) > 0
        assert isinstance(DESCRIPTION, str)
        assert len(DESCRIPTION) > 0

    def test_get_version_info(self):
        info = get_version_info()
        assert info["version"] == VERSION
        assert info["api_version"] == API_VERSION
        assert info["title"] == TITLE
        assert info["description"] == DESCRIPTION
        assert len(info) == 4
