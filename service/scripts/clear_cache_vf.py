"""清 flight.status 缓存 + variflight 负标，然后由外部重打验证。"""
import sqlite3

from app.config import data_dir
from app.core import negmark

d = data_dir()
c = sqlite3.connect(str(d / "cache.db"))
n = c.execute("DELETE FROM cache").rowcount
c.commit()
print("cache cleared:", n)
negmark.record_success(d / "negmark.db", "variflight", "flight.status")
negmark.record_success(d / "negmark.db", "variflight", "flight.price")
print("vf bans cleared")
