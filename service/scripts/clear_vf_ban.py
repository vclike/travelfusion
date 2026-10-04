"""清 variflight 负标（适配器修复后的冤案清理）。"""
from app.config import data_dir
from app.core import negmark

d = data_dir()
negmark.record_success(d / "negmark.db", "variflight", "flight.status")
negmark.record_success(d / "negmark.db", "variflight", "flight.price")
print("variflight bans cleared:",
      negmark.is_banned(d / "negmark.db", "variflight", "flight.status"),
      negmark.is_banned(d / "negmark.db", "variflight", "flight.price"))
