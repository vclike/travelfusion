"""一次性收编：所有 adapter 的本地 ProviderError → 统一 app.core.errors。幂等。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "app"
FILES = [
    ROOT / "providers" / n / "adapter.py"
    for n in ("airlabs", "aviationstack", "opensky", "travelpayouts",
              "amap", "openmeteo", "variflight", "googlemaps")
]
OLD = ('class ProviderError(Exception):\n'
       '    def __init__(self, code: str, hint: str = "", provider: str = ""):\n'
       '        self.code, self.hint, self.provider = code, hint, provider\n'
       '        super().__init__(f"{code}: {hint}")\n')
ANCHOR = "from __future__ import annotations\n"
NEW_IMPORT = ANCHOR + "\nfrom app.core.errors import ProviderError\n"

for f in FILES:
    t = f.read_text(encoding="utf-8")
    if "from app.core.errors import ProviderError" in t:
        print("skip (already unified):", f.name)
        continue
    t2 = t.replace(OLD, "", 1)
    if OLD in t:
        t2 = t2.replace(ANCHOR, NEW_IMPORT, 1)
        f.write_text(t2, encoding="utf-8")
        print("patched:", f.parent.name)
    else:
        print("!! local class NOT found in", f.parent.name,
              "— manual check needed")

# dispatch 换正主
dp = ROOT / "core" / "dispatch.py"
t = dp.read_text(encoding="utf-8")
t = t.replace("from app.providers.airlabs.adapter import ProviderError",
              "from app.core.errors import ProviderError", 1)
dp.write_text(t, encoding="utf-8")
print("dispatch unified")
