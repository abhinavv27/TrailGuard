import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api")))

from app.db.session import SessionLocal
from app.services.auth_service import AuthService

db = SessionLocal()
try:
    user = AuthService.authenticate_user("analyst@trailguard.ai", "demo1234", db)
    print("User authenticated:", user)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
