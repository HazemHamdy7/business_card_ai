from src.core.runtime.health_check import HealthCheck, HealthStatus


class TestHealthCheck:
    def setup_method(self) -> None:
        self.health = HealthCheck()

    def test_check_cuda(self) -> None:
        result = self.health.check_cuda()
        assert result.name == "cuda"
        assert result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

    def test_check_disk(self) -> None:
        result = self.health.check_disk()
        assert result.name == "disk"
        assert result.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY)

    def test_check_configuration(self) -> None:
        result = self.health.check_configuration()
        assert result.name == "configuration"

    def test_check_write_permissions(self) -> None:
        result = self.health.check_write_permissions()
        assert result.name == "write_permissions"
        assert result.passed

    def test_check_dataset(self) -> None:
        result = self.health.check_dataset()
        assert result.name == "dataset"

    def test_check_models(self) -> None:
        result = self.health.check_models()
        assert result.name == "models"

    def test_check_cache(self) -> None:
        result = self.health.check_cache()
        assert result.name == "cache"

    def test_run_all(self) -> None:
        results = self.health.run_all()
        assert len(results) == 7
        names = [r.name for r in results]
        assert "cuda" in names
        assert "disk" in names
        assert "configuration" in names
        assert "write_permissions" in names
        assert "dataset" in names
        assert "models" in names
        assert "cache" in names

    def test_run_selected(self) -> None:
        results = self.health.run_selected(["cuda", "disk"])
        assert len(results) == 2
        assert results[0].name == "cuda"
        assert results[1].name == "disk"

    def test_summary(self) -> None:
        summary = self.health.summary
        assert summary["total"] == 7
        assert "checks" in summary

    def test_health_check_result_to_dict(self) -> None:
        from src.core.runtime.health_check import HealthCheckResult, HealthStatus
        result = HealthCheckResult(name="test", status=HealthStatus.HEALTHY, message="OK")
        d = result.to_dict()
        assert d["name"] == "test"
        assert d["passed"] is True
