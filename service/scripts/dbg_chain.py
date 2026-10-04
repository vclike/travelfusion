"""调度链诊断：打印 chain，冻结免费源强制走 variflight，抓真实错误。"""
import json

from app.config import data_dir, load_settings
from app.core import dispatch, negmark, registry, keys

d = data_dir()
data = registry.load(d / "manifests.json")
chain = registry.active_chain(data, "flight.status", negmark_db=d / "negmark.db")
print("chain:", [(e["id"], e["tier"], e.get("costPerCall")) for e in chain])
print("vf key present:",
      bool((keys.load_keys(d).get("variflight") or {}).get("api_key")))

# 冻结免费源 → paid 路径必走 variflight
negmark.record_failure(d / "negmark.db", "airlabs", "flight.status", "debug-freeze")
negmark.record_failure(d / "negmark.db", "aviationstack", "flight.status", "debug-freeze")

out = dispatch.call_capability(
    "flight.status",
    {"flight_no": "CA165", "date": "2026-09-30",
     "policy": {"paid_calibrate": True, "confirm_spend": True}},
    data_dir=d, settings=load_settings())
print("attempted:", json.dumps(out.get("meta", {}).get("attempted"),
                               ensure_ascii=False))
print("sources:", out.get("meta", {}).get("sources"))
print("err:", json.dumps(out.get("error"), ensure_ascii=False))
print("data head:", json.dumps(out.get("data"), ensure_ascii=False)[:300])

# 清理诊断用负标
for pid in ("airlabs", "aviationstack", "variflight"):
    negmark.record_success(d / "negmark.db", pid, "flight.status")
print("debug bans cleared")
