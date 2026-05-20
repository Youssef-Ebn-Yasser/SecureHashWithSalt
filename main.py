from auth import AuthSystem

def data_menu(role):
    while True:
        print("\n==============================")
        print("        DATA MENU")
        print("==============================")
        print("[1] Show Normal Data")
        print("[2] Show Sensitive Data")
        print("[3] Logout / Go Back")
        
        choice = input("\nEnter Choice: ").strip()
        
        if choice == "1":
            print("\n*** NORMAL DATA ***")
            print("Here is the normal data...")
        elif choice == "2":
            if role == "Admin":
                print("\n*** SENSITIVE DATA ***")
                print("Here is the sensitive data...")
            else:
                print("\nAccess denied. You must be an Admin to view sensitive data.")
        elif choice == "3":
            print("\nLogging out / Going back...")
            break
        else:
            print("\nInvalid choice.")

def main():
    auth_system = AuthSystem()

    while True:

        print("\n==============================")
        print("        MAIN MENU")
        print("==============================")

        print("[1] Create New Account")
        print("[2] Login")
        print("[3] Login With Token")
        print("[4] Forget Password")
        print("[5] Exit")

        choice = input("\nEnter Choice: ").strip()

        # =====================================================
        # CREATE ACCOUNT
        # =====================================================
        if choice == "1":
            print("\n=== CREATE ACCOUNT ===")
            username = input("Enter UserName: ").strip()
            
            if auth_system.user_exists(username):
                print("\nThis user already exists.")
                continue

            password = input("Enter Password: ").strip()
            role = input("Enter Role (Admin/Normal): ").strip()

            success, msg = auth_system.create_account(username, password, role)
            print(f"\n{msg}")

        # =====================================================
        # LOGIN
        # =====================================================
        elif choice == "2":
            print("\n=== LOGIN ===")
            username = input("Enter UserName: ").strip()
            password = input("Enter Password: ").strip()

            success, msg, token, role = auth_system.login(username, password)
            if success:
                print(f"\n{msg}")
                print("Your Session Token:", token)
                data_menu(role)
            else:
                print(f"\n{msg}")

        # =====================================================
        # LOGIN WITH TOKEN
        # =====================================================
        elif choice == "3":
            print("\n=== LOGIN WITH TOKEN ===")
            token = input("Enter session token: ").strip()

            success, msg, role = auth_system.login_with_token(token)
            if success:
                print(f"\n{msg}")
                data_menu(role)
            else:
                print(f"\n{msg}")

        # =====================================================
        # FORGET PASSWORD
        # =====================================================
        elif choice == "4":
            print("\n=== FORGET PASSWORD ===")
            username = input("Enter UserName: ").strip()
            
            if not auth_system.user_exists(username):
                print("\nUser does not exist.")
                continue

            secret = input("Enter secret: ").strip()
            
            if secret == "root":
                new_password = input("Enter New Password: ").strip()
                success, msg = auth_system.reset_password(username, secret, new_password)
                print(f"\n{msg}")
            else:
                print("\nInvalid secret.")

        # =====================================================
        # EXIT
        # =====================================================
        elif choice == "5":
            token = input("Enter session token to delete (or press Enter to skip): ").strip()
            if token:
                success, msg = auth_system.invalidate_token(token)
                print(f"\n{msg}")
            
            print("\nProgram closed.")
            break

        else:
            print("\nInvalid choice.")

if __name__ == "__main__":
    main()