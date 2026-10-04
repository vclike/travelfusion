"""运行时 manifest 增量升级器（幂等）——种子新条目/状态修正后跑一次。"""
import json

P = "/app/data/manifests.json"
d = json.load(open(P))
provs = d["providers"]


def upsert(entry: dict) -> None:
    for i, x in enumerate(provs):
        if x["id"] == entry["id"]:
            provs[i].update(entry)
            return
    provs.append(entry)


upsert({"id": "variflight", "status": "active", "tier": "paid",
        "costPerCall": 0.5,
        "capabilities": ["flight.status", "flight.price"],
        "auth": "header:X-API-Key", "key_configured": True,
        "verifiedAt": "2026-09-30",
        "quota": {"period": "total", "limit": None, "mode": "paygo"},
        "notes": "官方 Aviation MCP；付费校准源（仅 paid_calibrate 被调度）"})
upsert({"id": "openmeteo", "status": "active", "tier": "free", "costPerCall": 0,
        "capabilities": ["weather.context"], "auth": "none",
        "key_configured": True, "verifiedAt": "2026-09-30",
        "quota": {"period": "total", "limit": None, "mode": "unlimited"},
        "notes": "Open-Meteo 无 key；双层天气"})
upsert({"id": "googlemaps", "status": "active", "tier": "free", "costPerCall": 0,
        "capabilities": ["ground.route.intl"], "auth": "query_param:key",
        "key_configured": True, "verifiedAt": "2026-09-30",
        "quota": {"period": "month", "limit": 20000, "mode": "monthly"},
        "notes": "境外地面交通（高德境内互补）；WGS-84 零转换"})
for x in provs:
    if x["id"] == "amap":
        x["status"] = "active"                    # route_ground 已上线

json.dump(d, open(P, "w"), ensure_ascii=False, indent=2)
print("ids:", [x["id"] for x in provs])
print("statuses:", [(x["id"], x["status"]) for x in provs])
