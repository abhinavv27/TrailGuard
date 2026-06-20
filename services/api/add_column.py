from app.db.session import engine
from sqlalchemy import text
import traceback

try:
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE graph_metrics ADD COLUMN metrics_json JSON;'))
        conn.commit()
    print("Success")
except Exception as e:
    print(traceback.format_exc())
