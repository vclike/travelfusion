"""清 googlemaps 负标（legacy→v2 迁移期间的历史冤案）。"""
from app.config import data_dir
from app.core import negmark

d = data_dir()
negmark.record_success(d / "negmark.db", "googlemaps", "ground.route.intl")
print("googlemaps banned:",
      negmark.is_banned(d / "negmark.db", "googlemaps", "ground.route.intl"))
