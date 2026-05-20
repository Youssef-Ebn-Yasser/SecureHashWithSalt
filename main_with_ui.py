import tkinter as tk
from tkinter import messagebox, simpledialog
from auth import AuthSystem

class PasswordDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)
        
        dialog_width = 300
        dialog_height = 120
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (dialog_width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (dialog_height // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, False)
        self.result = None
        
        tk.Label(self, text=prompt).pack(pady=10)
        self.entry = tk.Entry(self, show="*")
        self.entry.pack(pady=5)
        self.entry.focus_set()
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", command=self.on_ok, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(side="left", padx=5)
        
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
        
    def on_ok(self):
        val = self.entry.get()
        self.result = val.strip() if val else None
        self.destroy()

def ask_password(parent, title, prompt):
    d = PasswordDialog(parent, title, prompt)
    return d.result

class AppUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Security Project - UI")
        
        window_width = 350
        window_height = 450
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)
        
        self.auth_system = AuthSystem()
        self.current_role = None
        self.current_token = None
        
        self.main_frame = tk.Frame(self)
        self.data_frame = tk.Frame(self)
        
        self.setup_main_menu()
        self.setup_data_menu()
        
        self.show_main_menu()

    def setup_main_menu(self):
        tk.Label(self.main_frame, text="MAIN MENU", font=("Helvetica", 16, "bold")).pack(pady=30)
        
        btn_config = {'width': 25, 'pady': 5, 'font': ("Helvetica", 10)}
        tk.Button(self.main_frame, text="Create New Account", command=self.create_account, **btn_config).pack(pady=5)
        tk.Button(self.main_frame, text="Login", command=self.login, **btn_config).pack(pady=5)
        tk.Button(self.main_frame, text="Login With Token", command=self.login_with_token, **btn_config).pack(pady=5)
        tk.Button(self.main_frame, text="Forget Password", command=self.forget_password, **btn_config).pack(pady=5)
        tk.Button(self.main_frame, text="Exit", command=self.exit_app, **btn_config).pack(pady=5)

    def setup_data_menu(self):
        tk.Label(self.data_frame, text="DATA MENU", font=("Helvetica", 16, "bold")).pack(pady=30)
        
        btn_config = {'width': 25, 'pady': 5, 'font': ("Helvetica", 10)}
        tk.Button(self.data_frame, text="Show Normal Data", command=self.show_normal_data, **btn_config).pack(pady=5)
        tk.Button(self.data_frame, text="Show Sensitive Data", command=self.show_sensitive_data, **btn_config).pack(pady=5)
        tk.Button(self.data_frame, text="Logout / Go Back", command=self.logout, **btn_config).pack(pady=30)

    def show_main_menu(self):
        self.data_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self.current_role = None
        self.current_token = None

    def show_data_menu(self, role, token):
        self.current_role = role
        self.current_token = token
        self.main_frame.pack_forget()
        self.data_frame.pack(fill="both", expand=True)

    # --- Main Menu Actions ---
    def create_account(self):
        username = simpledialog.askstring("Create Account", "Enter UserName:", parent=self)
        if not username or not username.strip():
            return
        username = username.strip()
            
        if self.auth_system.user_exists(username):
            messagebox.showerror("Error", "This user already exists.")
            return

        password = ask_password(self, "Create Account", "Enter Password:")
        if not password or not password.strip():
            return
        password = password.strip()
            
        role = simpledialog.askstring("Create Account", "Enter Role (Admin/Normal):", parent=self)
        if not role or not role.strip():
            return
        role = role.strip()

        success, msg = self.auth_system.create_account(username, password, role)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

    def login(self):
        username = simpledialog.askstring("Login", "Enter UserName:", parent=self)
        if not username or not username.strip():
            return
        username = username.strip()
            
        password = ask_password(self, "Login", "Enter Password:")
        if not password or not password.strip():
            return
        password = password.strip()

        success, msg, token, role = self.auth_system.login(username, password)
        if success:
            self.clipboard_clear()
            self.clipboard_append(token)
            self.update() 
            messagebox.showinfo("Success", f"{msg}\n\nYour Session Token has been copied to clipboard:\n{token}")
            self.show_data_menu(role, token)
        else:
            messagebox.showerror("Error", msg)

    def login_with_token(self):
        token = simpledialog.askstring("Login with Token", "Enter session token:", parent=self)
        if not token or not token.strip():
            return
        token = token.strip()

        success, msg, role = self.auth_system.login_with_token(token)
        if success:
            messagebox.showinfo("Success", msg)
            self.show_data_menu(role, token)
        else:
            messagebox.showerror("Error", msg)

    def forget_password(self):
        username = simpledialog.askstring("Forget Password", "Enter UserName:", parent=self)
        if not username or not username.strip():
            return
        username = username.strip()
            
        if not self.auth_system.user_exists(username):
            messagebox.showerror("Error", "User does not exist.")
            return

        secret = ask_password(self, "Forget Password", "Enter secret (Hint: root):")
        if not secret or not secret.strip():
            return
        secret = secret.strip()
            
        if secret == "root":
            new_password = ask_password(self, "Forget Password", "Enter New Password:")
            if not new_password or not new_password.strip():
                return
            new_password = new_password.strip()

            success, msg = self.auth_system.reset_password(username, secret, new_password)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
        else:
            messagebox.showerror("Error", "Invalid secret.")

    def exit_app(self):
        token = simpledialog.askstring("Exit", "Enter session token to delete (or leave empty to skip):", parent=self)
        if token and token.strip():
            token = token.strip()
            success, msg = self.auth_system.invalidate_token(token)
            messagebox.showinfo("Token Deletion", msg)
        self.destroy()

    # --- Data Menu Actions ---
    def show_normal_data(self):
        messagebox.showinfo("Normal Data", "*** NORMAL DATA ***\nHere is the normal data...")

    def show_sensitive_data(self):
        if self.current_role == "Admin":
            messagebox.showinfo("Sensitive Data", "*** SENSITIVE DATA ***\nHere is the sensitive data...")
        else:
            messagebox.showerror("Access Denied", "Access denied. You must be an Admin to view sensitive data.")

    def logout(self):
        self.show_main_menu()

if __name__ == "__main__":
    app = AppUI()
    app.mainloop()
