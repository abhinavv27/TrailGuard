import traceback
from app.db.session import SessionLocal
from app.api.v1.accounts import get_account

try:
    db = SessionLocal()
    account_id = 'b55172c0-3587-46d9-8069-4df1960e7510'
    res = get_account(account_id=account_id, current_user={'sub': 'analyst'}, db=db)
    print("Success")
except Exception as e:
    print(traceback.format_exc())
