"""dispatch 层 transit 查询诊断：打印 error + attempted。"""
import json

from app.config import data_dir, load_settings
from app.core import dispatch

out = dispatch.call_capability(
    "ground.route.intl",
    {"origin_wgs": [139.6503, 35.6762],
     "destination_wgs": [135.5023, 34.6937],
     "mode": "transit", "policy": {}},
    data_dir=data_dir(), settings=load_settings())
print("err:", json.dumps(out.get("error"), ensure_ascii=False))
print("attempted:", json.dumps(out.get("meta", {}).get("attempted"),
                               ensure_ascii=False))
print("sources:", out.get("meta", {}).get("sources"))
