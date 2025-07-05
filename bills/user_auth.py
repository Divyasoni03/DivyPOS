import json
import os
from tkinter import Tk, Toplevel, Label, Entry, Button, messagebox, simpledialog

CONFIG_FILE = "user_config.json"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def set_pin(role):
    def save():
        p1 = pin_entry.get()
        p2 = confirm_entry.get()
        if not p1 or not p2:
            messagebox.showerror("Error", "Both fields are required.")
        elif p1 != p2:
            messagebox.showerror("Error", "PINs do not match.")
        else:
            config = load_config()
            config[f"{role}_pin"] = p1
            save_config(config)
            messagebox.showinfo("Success", f"{role.title()} PIN set successfully.")
            win.destroy()

    win = Toplevel()
    win.title(f"Set {role.title()} PIN")
    win.geometry("300x150")
    win.grab_set()

    Label(win, text="New PIN:").pack()
    pin_entry = Entry(win, show="*")
    pin_entry.pack()

    Label(win, text="Confirm PIN:").pack()
    confirm_entry = Entry(win, show="*")
    confirm_entry.pack()

    Button(win, text="Save PIN", command=save).pack(pady=5)

def verify_user(role_required="user"):
    config = load_config()
    key = f"{role_required}_pin"

    if not config.get(key):
        set_pin(role_required)
        return False

    access_granted = [False]

    def verify():
        entered = entry.get()
        if entered == config.get(key):
            access_granted[0] = True
            win.destroy()
        else:
            messagebox.showerror("Error", "Incorrect PIN.")

    def forgot():
        answer = simpledialog.askstring("Security Check", "Enter reset code (hint: 1234):")
        if answer == "1234":
            set_pin(role_required)
            win.destroy()
        else:
            messagebox.showerror("Error", "Incorrect reset code.")

    win = Toplevel()
    win.title(f"{role_required.title()} Login")
    win.geometry("300x150")
    win.grab_set()

    Label(win, text=f"Enter {role_required.title()} PIN:").pack()
    entry = Entry(win, show="*", width=20)
    entry.pack()

    Button(win, text="Verify", command=verify).pack(pady=5)
    Button(win, text="Forgot PIN?", command=forgot).pack()

    win.wait_window()
    return access_granted[0]

# 🟢 Main entry point: verifying USER role
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide main window
    result = verify_user("user")  # 👈 focus here on "user" role

    if result:
        messagebox.showinfo("Access Granted", "Welcome User! ✅")
    else:
        messagebox.showinfo("Access Denied", "Access not granted. ❌")

    root.mainloop()
