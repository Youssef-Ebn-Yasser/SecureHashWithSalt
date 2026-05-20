from datetime import datetime, timedelta
from access_db import PasswordDatabase
from hash_algorithm import HashAlgorithm
from token_manager import TokenManager
import json
from constants import UserColumns

class AuthSystem:
    def __init__(self):
        self.db = PasswordDatabase()
        self.hasher = HashAlgorithm()
        self.token_manager = TokenManager(expire_minutes=30)
        
    def load_data(self):
        with open(self.db.file_path, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.db.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def can_unblock(self, user):
        if user[UserColumns.BLOCKED_DATE] == "" or user[UserColumns.BLOCKED_DATE] is None:
            return False

        blocked_time = datetime.fromisoformat(user[UserColumns.BLOCKED_DATE])
        return datetime.now() - blocked_time >= timedelta(seconds=30)

    def find_user(self, data, username):
        for u in data:
            if u[UserColumns.USERNAME] == username:
                return u
        return None

    def user_exists(self, username):
        data = self.load_data()
        return self.find_user(data, username) is not None

    def create_account(self, username, password, role):
        data = self.load_data()
        
        if self.find_user(data, username):
            return False, "This user already exists."

        hash_password = self.hasher.hash(password)

        new_user = {
            UserColumns.USERNAME: username,
            UserColumns.ROLE: role,
            UserColumns.HASH_PASSWORD: hash_password,
            UserColumns.IS_BLOCKED: False,
            UserColumns.NUMBER_OF_FAILED: 0,
            UserColumns.BLOCKED_DATE: "",
            UserColumns.SESSION_TOKEN: "",
            UserColumns.TOKEN_EXPIRE_DATE: ""
        }

        data.append(new_user)
        self.save_data(data)
        
        return True, "Account created successfully."

    def login(self, username, password):
        data = self.load_data()
        user = self.find_user(data, username)

        if not user:
            return False, "User does not exist.", None, None

        if user[UserColumns.IS_BLOCKED]:
            if self.can_unblock(user):
                user[UserColumns.IS_BLOCKED] = False
                user[UserColumns.NUMBER_OF_FAILED] = 0
                user[UserColumns.BLOCKED_DATE] = ""
                self.save_data(data)
                print("\nAccount unblocked.")
            else:
                return False, "Account is blocked.", None, None

        if not self.hasher.verify(password, user[UserColumns.HASH_PASSWORD]):
            user[UserColumns.NUMBER_OF_FAILED] += 1
            if user[UserColumns.NUMBER_OF_FAILED] >= 3:
                user[UserColumns.IS_BLOCKED] = True
                user[UserColumns.BLOCKED_DATE] = datetime.now().isoformat()
                self.save_data(data)
                print("\nWrong password.")
                return False, "Account blocked for 30 seconds.", None, None
            
            self.save_data(data)
            return False, "Wrong password.", None, None

        user[UserColumns.NUMBER_OF_FAILED] = 0

        session = self.token_manager.generate_token()
        user[UserColumns.SESSION_TOKEN] = session["token"]
        user[UserColumns.TOKEN_EXPIRE_DATE] = session["expire_date"].isoformat()

        self.save_data(data)

        return True, "Login successful.", user[UserColumns.SESSION_TOKEN], user[UserColumns.ROLE]

    def login_with_token(self, token):
        data = self.load_data()
        user = None
        for u in data:
            if u[UserColumns.SESSION_TOKEN] == token:
                user = u
                break

        if not user:
            return False, "Invalid token.", None

        if user[UserColumns.IS_BLOCKED]:
            if self.can_unblock(user):
                user[UserColumns.IS_BLOCKED] = False
                user[UserColumns.NUMBER_OF_FAILED] = 0
                user[UserColumns.BLOCKED_DATE] = ""
                self.save_data(data)
                print("\nAccount unblocked.")
            else:
                return False, "Account is blocked.", None

        expire_date = user[UserColumns.TOKEN_EXPIRE_DATE]

        if expire_date == "" or expire_date is None:
            return False, "Invalid session.", None

        expire_time = datetime.fromisoformat(expire_date)

        if datetime.now() > expire_time:
            user[UserColumns.SESSION_TOKEN] = ""
            user[UserColumns.TOKEN_EXPIRE_DATE] = ""
            self.save_data(data)
            return False, "Token expired.", None

        return True, "Token login success!", user[UserColumns.ROLE]

    def reset_password(self, username, secret, new_password):
        if secret != "root":
            return False, "Invalid secret."
        
        data = self.load_data()
        user = self.find_user(data, username)
        
        if not user:
            return False, "User does not exist."

        if user[UserColumns.IS_BLOCKED]:
            if self.can_unblock(user):
                user[UserColumns.IS_BLOCKED] = False
                user[UserColumns.NUMBER_OF_FAILED] = 0
                user[UserColumns.BLOCKED_DATE] = ""
                self.save_data(data)
                print("\nAccount unblocked.")
            else:
                return False, "Account is blocked. Cannot reset password at this time."
            
        hash_password = self.hasher.hash(new_password)
        user[UserColumns.HASH_PASSWORD] = hash_password
        
        # Reset failed attempts and unblock
        user[UserColumns.IS_BLOCKED] = False
        user[UserColumns.NUMBER_OF_FAILED] = 0
        user[UserColumns.BLOCKED_DATE] = ""
        
        # Invalidate old sessions
        user[UserColumns.SESSION_TOKEN] = ""
        user[UserColumns.TOKEN_EXPIRE_DATE] = ""
        
        self.save_data(data)
        
        return True, "Password reset successfully."

    def invalidate_token(self, token):
        data = self.load_data()
        user = None
        for u in data:
            if u[UserColumns.SESSION_TOKEN] == token:
                user = u
                break
                
        if not user:
            return False, "Invalid token or token already deleted."
            
        user[UserColumns.SESSION_TOKEN] = ""
        user[UserColumns.TOKEN_EXPIRE_DATE] = ""
        self.save_data(data)
        
        return True, "Token deleted successfully."
