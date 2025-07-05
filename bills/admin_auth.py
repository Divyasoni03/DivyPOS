import json
import os
from tkinter import Tk, Toplevel, Label, Entry, Button, messagebox

CONFIG_FILE = "admin_config.json"

# Save the PIN to JSON file
def save_pin(pin):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"pin": pin}, f)

# Load the PIN from JSON file
def load_pin():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("pin")
    return None

# Set a new PIN (if not already set)
def set_new_pin():
    def save():
        p1 = pin_entry.get()
        p2 = confirm_entry.get()
        if not p1 or not p2:
            messagebox.showerror("Error", "Enter both fields.")
        elif p1 != p2:
            messagebox.showerror("Error", "PINs do not match.")
        else:
            save_pin(p1)
            messagebox.showinfo("Success", "PIN set successfully.")
            win.destroy()

    win = Toplevel()
    win.title("🔐 Set Admin PIN")
    win.geometry("300x150")
    win.grab_set()

    Label(win, text="Enter New PIN:").pack(pady=5)
    pin_entry = Entry(win, show="*")
    pin_entry.pack()

    Label(win, text="Confirm PIN:").pack(pady=5)
    confirm_entry = Entry(win, show="*")
    confirm_entry.pack()

    Button(win, text="✅ Save PIN", command=save).pack(pady=10)

# Verify admin by asking for PIN
def verify_admin():
    pin = load_pin()
    if not pin:
        set_new_pin()
        return False

    access_granted = [False]

    def check():
        if entry.get() == pin:
            access_granted[0] = True
            win.destroy()
        else:
            messagebox.showerror("❌ Error", "Incorrect PIN.")

    def forgot():
        if messagebox.askyesno("Forgot PIN", "Are you sure you want to reset the PIN?"):
            try:
                os.remove(CONFIG_FILE)
                messagebox.showinfo("Reset Done", "PIN removed. Set new PIN now.")
                win.destroy()
                set_new_pin()
            except:
                messagebox.showerror("Error", "Could not reset PIN.")

    win = Toplevel()
    win.title("🔐 Admin Login")
    win.geometry("300x150")
    win.grab_set()

    Label(win, text="Enter Admin PIN:").pack(pady=5)
    entry = Entry(win, show="*", width=20)
    entry.pack()

    Button(win, text="🔓 Verify", command=check).pack(pady=5)
    Button(win, text="❓ Forgot PIN?", command=forgot).pack(pady=2)

    win.wait_window()
    return access_granted[0]

# Main Execution Block
if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the root window
    result = verify_admin()

    # If access granted, show a success popup
    if result:
        messagebox.showinfo("Access Granted", "Welcome Admin! ✅")
    else:
        messagebox.showinfo("Access Denied", "No access granted. ❌")

    root.mainloop()
