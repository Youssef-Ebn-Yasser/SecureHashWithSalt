import json
import os
from constants import UserColumns

class PasswordDatabase:

    def __init__(self):

        # Folder name
        self.folder_name = "Data"

        # File name (JSON instead of CSV)
        self.file_name = "passwords_db.json"

        # Full path
        self.file_path = os.path.join(self.folder_name, self.file_name)

        # Create folder if not exists
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

        # Create JSON file if not exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    # =====================================================
    # Load Data
    # =====================================================
    def _load_data(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    # =====================================================
    # Save Data
    # =====================================================
    def _save_data(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    # =====================================================
    # Insert New User
    # =====================================================
    def insert_user(self, username, role, hash_password):

        data = self._load_data()

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

        self._save_data(data)

        print("User inserted successfully.")

    # =====================================================
    # Get User By Username
    # =====================================================
    def get_user(self, username):

        data = self._load_data()

        for user in data:
            if user[UserColumns.USERNAME] == username:
                return {
                    UserColumns.ROLE: user[UserColumns.ROLE],
                    UserColumns.HASH_PASSWORD: user[UserColumns.HASH_PASSWORD],
                    UserColumns.IS_BLOCKED: user[UserColumns.IS_BLOCKED],
                    UserColumns.NUMBER_OF_FAILED: user[UserColumns.NUMBER_OF_FAILED],
                    UserColumns.BLOCKED_DATE: user[UserColumns.BLOCKED_DATE],
                    UserColumns.SESSION_TOKEN: user[UserColumns.SESSION_TOKEN],
                    UserColumns.TOKEN_EXPIRE_DATE: user[UserColumns.TOKEN_EXPIRE_DATE]
                }
        return None