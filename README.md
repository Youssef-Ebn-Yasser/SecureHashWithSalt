# SecureHashWithSalt

A robust, pure Python authentication system featuring a custom-built cryptographic hash algorithm. This project demonstrates secure password storage, session management, role-based access control, and account lockouts without relying on external cryptographic libraries (other than the standard `secrets` module for secure comparisons).

It features both a **Command-Line Interface (CLI)** and a **Graphical User Interface (GUI)**.

## Key Features

1. **Custom Hashing Algorithm (`hash_algorithm.py`)**
   - Implements a custom cryptographic hash function heavily inspired by the Merkle-Damgård construction and SHA-256.
   - Operates entirely in pure Python, demonstrating bitwise operations, padding, block creation (512-bit blocks), word expansion, and a 64-round compression loop.
   - **Salt Generation**: Automatically generates a 16-character cryptographic salt for every new password. The salt is concatenated with the password before hashing, effectively mitigating rainbow table attacks.
   - **Secure Verification**: Uses `secrets.compare_digest` to prevent timing attacks during password validation.
   - **Format**: Stored in the database as `salt$hash`.

2. **Authentication & Session Management (`auth.py` & `token_manager.py`)**
   - **Login Flows**: Supports both standard username/password login and Token-based session logins.
   - **Account Lockouts**: Temporarily blocks an account for 30 seconds after 3 consecutive failed login attempts to prevent brute-force attacks.
   - **Session Expiry**: Successfully logging in generates a time-limited session token.
   - **Password Resets**: Includes a "Forget Password" flow protected by a master secret.

3. **Role-Based Access Control (RBAC)**
   - Distinguishes between `Admin` and `Normal` users.
   - Sensitive Data can only be accessed if the currently authenticated user session possesses the `Admin` role.

4. **Dual Interfaces**
   - **`main.py`**: A fully functional, interactive command-line application.
   - **`main_with_ui.py`**: A clean, centered `tkinter` Graphical User Interface featuring masked password dialogs and clipboard integration for session tokens.

5. **JSON Flat-File Database (`access_db.py` & `constants.py`)**
   - Stores users securely in a JSON format (`Data/passwords_db.json`), cleanly referenced throughout the codebase using strongly-typed static variables to prevent string typos.

## How to Run

### Command-Line Interface (CLI)
Run the standard console application:
```bash
python main.py
```

### Graphical User Interface (GUI)
Run the Tkinter-based graphical interface:
```bash
python main_with_ui.py
```

## Structure overview
- `hash_algorithm.py`: The custom hashing and salting engine.
- `auth.py`: The authentication controller orchestrating login logic, block checks, and token issuing.
- `access_db.py`: The JSON database interface.
- `constants.py`: Holds the `UserColumns` constants to standardize database dictionary keys.
- `token_manager.py`: Handles generation of secure, expiring tokens.
- `main.py` & `main_with_ui.py`: The frontend entry points.
