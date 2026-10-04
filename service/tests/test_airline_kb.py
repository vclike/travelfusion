import pytest

from app.core import airline_kb

KB = {
    "airlines": [
        {"iata": "CA", "icao": "CCA", "name_cn": "中国国际航空",
         "aliases": ["国航", "Air China"], "carrier_type": "full_service",
         "hints": [], "revisions": []},
    ]
}


@pytest.fixture
def kb_path(tmp_path):
    p = tmp_path / "airlines_kb.yaml"
    p.write_text(yaml_dump(KB), encoding="utf-8")
    return p


def yaml_dump(data) -> str:
    import yaml
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def test_find_by_alias_chinese(kb_path):
    assert airline_kb.find_by_alias(kb_path, "国航")["iata"] == "CA"
    assert airline_kb.find_by_alias(kb_path, "air china")["iata"] == "CA"
    assert airline_kb.find_by_alias(kb_path, "春秋") is None


def test_set_appends_revision_not_overwrite(kb_path):
    e = airline_kb.set_airline(
        kb_path, {"iata": "CA", "hints": [{"tag": "餐食", "text": "正餐免费"}]},
        by="agent", reason="用户实测补充")
    assert e["hints"] == [{"tag": "餐食", "text": "正餐免费"}]
    assert e["revisions"][-1]["by"] == "agent"
    assert e["revisions"][-1]["reason"] == "用户实测补充"
    assert len(e["revisions"]) == 1


def test_set_requires_reason_and_valid_by(kb_path):
    with pytest.raises(ValueError):
        airline_kb.set_airline(kb_path, {"iata": "CA"}, by="agent", reason="")
    with pytest.raises(ValueError):
        airline_kb.set_airline(kb_path, {"iata": "CA"}, by="nobody", reason="x")


def test_set_new_airline_creates(kb_path):
    e = airline_kb.set_airline(
        kb_path, {"iata": "9C", "name_cn": "春秋航空", "carrier_type": "low_cost"},
        by="agent", reason="调研蒸馏")
    assert e["name_cn"] == "春秋航空"
    assert airline_kb.get_airline(kb_path, "9c")["iata"] == "9C"   # 大小写归一


def test_add_alias(kb_path):
    e = airline_kb.add_alias(kb_path, "CA", "AVIC Air China",
                             by="agent", reason="新平台别名发现")
    assert "AVIC Air China" in e["aliases"]
    assert airline_kb.find_by_alias(kb_path, "avic air china")["iata"] == "CA"


def test_unset_hint(kb_path):
    airline_kb.set_airline(
        kb_path, {"iata": "CA", "hints": [{"tag": "餐食", "text": "x"}]},
        by="agent", reason="测试")
    e = airline_kb.unset_hint(kb_path, "CA", "餐食", by="agent", reason="标记有误")
    assert e["hints"] == []


def test_set_norm(kb_path, tmp_path):
    norms_path = tmp_path / "norms.yaml"
    norms = airline_kb.set_norm(norms_path, "cn_carry_on", "5–8kg",
                                by="agent", reason="调研基线")
    assert norms["cn_carry_on"] == "5–8kg"
    with pytest.raises(ValueError):
        airline_kb.set_norm(norms_path, "x", "y", by="agent", reason="")
