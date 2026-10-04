"""服务鉴权测试：MCP API key 中间件 + 管理操作密码门。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mcp_server import provider_admin, airline_kb

client = TestClient(app)


def test_mcp_requires_api_key(monkeypatch):
    monkeypatch.setenv("TF_MCP_API_KEY", "secret-mcp-key")
    with TestClient(app) as c:
        r = c.post("/mcp", json={"jsonrpc": "2.0", "method": "initialize",
                                 "params": {}})
        assert r.status_code == 401
        r2 = c.post("/mcp", json={"jsonrpc": "2.0", "method": "initialize",
                                  "params": {}},
                    headers={"X-API-Key": "secret-mcp-key"})
        assert r2.status_code != 401
        r3 = c.post("/mcp?key=secret-mcp-key",
                    json={"jsonrpc": "2.0", "method": "initialize", "params": {}})
        assert r3.status_code != 401        # query 参数同样放行
    assert True


def test_health_stays_open(monkeypatch):
    monkeypatch.setenv("TF_MCP_API_KEY", "secret-mcp-key")
    r = client.get("/health")
    assert r.status_code == 200


def test_admin_gate_blocks_mutation(monkeypatch, tmp_path):
    monkeypatch.setenv("TF_ADMIN_KEY", "admin-secret")
    out = provider_admin("enable", provider="x", admin_key="wrong")
    assert out["error"]["code"] == "AUTH_REQUIRED"
    out2 = airline_kb("set", iata="XX", patch={"iata": "XX"}, admin_key="wrong")
    assert out2["error"]["code"] == "AUTH_REQUIRED"


def test_admin_gate_allows_list_without_key(monkeypatch):
    monkeypatch.setenv("TF_ADMIN_KEY", "admin-secret")
    out = provider_admin("list")
    assert "error" not in out or out["error"] is None


def test_admin_gate_opens_when_unconfigured(monkeypatch):
    import app.core.keys as keys_mod
    import app.mcp_server as ms
    monkeypatch.setattr(keys_mod, "auth_config",
                        lambda dd: {"mcp_api_key": None, "admin_key": None})
    assert ms._require_admin("whatever") is None
