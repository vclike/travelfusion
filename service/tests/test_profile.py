"""profile.yaml（出行档案）单元测试。"""
from pathlib import Path

import pytest

from app.core import profile


def test_save_and_load_roundtrip(tmp_path):
    doc = profile.save_profile(tmp_path, {"addresses": [
        {"alias": "家", "text": "军安卫士花园"},
        {"alias": "公司", "text": "天府软件园C区"},
    ]}, by="test")
    assert doc["updated_by"] == "test"
    assert len(doc["addresses"]) == 2
    back = profile.load_profile(tmp_path)
    assert back["addresses"][0] == {"alias": "家", "text": "军安卫士花园"}


def test_resolve_alias_exact(tmp_path):
    profile.save_profile(tmp_path,
                         {"addresses": [{"alias": "家", "text": "军安卫士花园"}]})
    assert profile.resolve_alias(tmp_path, "家") == ("军安卫士花园", "家")
    assert profile.resolve_alias(tmp_path, "家 ") == ("军安卫士花园", "家")
    assert profile.resolve_alias(tmp_path, "公司") is None
    assert profile.resolve_alias(tmp_path, "") is None


def test_save_rejects_duplicates_over_limit_and_missing(tmp_path):
    with pytest.raises(ValueError):
        profile.save_profile(tmp_path, {"addresses": [
            {"alias": "家", "text": "a"}, {"alias": "家", "text": "b"}]})
    with pytest.raises(ValueError):
        profile.save_profile(tmp_path, {"addresses": [
            {"alias": f"x{i}", "text": "t"} for i in range(9)]})
    with pytest.raises(ValueError):
        profile.save_profile(tmp_path, {"addresses": [{"alias": "a"}]})


def test_load_missing_file_is_empty(tmp_path):
    p = profile.load_profile(Path(tmp_path))
    assert p["addresses"] == []
    assert profile.resolve_alias(Path(tmp_path), "家") is None
