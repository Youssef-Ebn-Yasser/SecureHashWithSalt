import uuid
from datetime import datetime, timedelta


class TokenManager:

    def __init__(self, expire_minutes=30):
        # default token lifetime
        self.expire_minutes = expire_minutes


    def generate_token(self):
        token = str(uuid.uuid4())
        expire_date = datetime.now() + timedelta(minutes=self.expire_minutes)

        return {
            "token": token,
            "expire_date": expire_date
        }
