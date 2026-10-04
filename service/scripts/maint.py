"""容器内维护脚本：清负标 + 手动跑一轮采集 + 打印基线行。"""
from app.config import data_dir
from app.core import baseline, collector, negmark

d = data_dir()
negmark.record_success(d / "negmark.db", "travelpayouts", "flight.price")
print("travelpayouts ban cleared")
s = collector.collect_once(d)
print("collect:", s)
import sqlite3
c = sqlite3.connect(str(d / "baseline.db"))
rows = c.execute("SELECT origin,dest,price,currency,airline FROM baseline").fetchall()
print("baseline rows:", len(rows))
for r in rows[:10]:
    print(" ", r)
