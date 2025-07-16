import tkinter as tk
from tkinter import messagebox
import time
import threading

class AuthCodeApp:
    def __init__(self, master):
        """
        Initializes the main application window and widgets.
        Args:
            master: The root Tkinter window.
        """
        self.master = master
        master.title("Kisan Card Authentication")
        master.geometry("500x400") # Set initial window size
        master.resizable(False, False) # Make window non-resizable
        master.configure(bg="#DDE40A") # Background color for the main window

        # Center the window on the screen
        self.center_window()

        # Create a frame for the card-like appearance
        self.card_frame = tk.Frame(master, bg="white", bd=8, relief="raised",
                                   highlightbackground="#0AD03F", highlightthickness=2)
        self.card_frame.pack(pady=50, padx=24, fill="both", expand=True)

        # Title Label
        self.title_label = tk.Label(self.card_frame,
                                    text="Kisan Card Authentication",
                                    font=("Arial", 22, "bold"),
                                    fg="#0AD03F",
                                    bg="white")
        self.title_label.pack(pady=(20, 30))

        # Entry for the 12-digit code
        self.code_var = tk.StringVar()
        self.code_var.trace_add("write", self._check_code_length) # Real-time validation

        self.code_entry = tk.Entry(self.card_frame,
                                   textvariable=self.code_var,
                                   font=("Arial", 16),
                                   width=25,
                                   bd=2,
                                   relief="solid",
                                   justify="center")
        self.code_entry.pack(pady=10)
        self.code_entry.bind("<KeyRelease>", self._limit_entry_length) # Limit input length

        # Label for input instructions
        self.instruction_label = tk.Label(self.card_frame,
                                          text="Enter 12 Digit number in Kisan Card",
                                          font=("Arial", 12),
                                          fg="gray",
                                          bg="white")
        self.instruction_label.pack(pady=(0, 10))

        # Validation icon (initially hidden)
        self.valid_icon_label = tk.Label(self.card_frame, text="", font=("Arial", 20), bg="white")
        self.valid_icon_label.pack()

        # Loading indicator/message
        self.loading_label = tk.Label(self.card_frame, text="", font=("Arial", 14), fg="blue", bg="white")
        self.loading_label.pack(pady=10)

        # Verify Button
        self.verify_button = tk.Button(self.card_frame,
                                       text="Verify",
                                       command=self._verify_code_threaded, # Use threaded version
                                       font=("Arial", 18, "bold"),
                                       bg="#29B927", # Background color
                                       fg="white",    # Text color
                                       activebackground="#0AD03F", # Active background color
                                       activeforeground="white", # Active text color
                                       relief="raised",
                                       bd=4,
                                       padx=20,
                                       pady=8)
        self.verify_button.pack(pady=20)

        self._is_code_valid = False

    def center_window(self):
        """Centers the main window on the screen."""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def _limit_entry_length(self, event=None):
        """Limits the entry widget to 12 characters."""
        if len(self.code_var.get()) > 12:
            self.code_var.set(self.code_var.get()[:12])

    def _check_code_length(self, *args):
        """
        Checks the length of the entered code and updates the validation icon.
        """
        code = self.code_var.get()
        if code.isdigit() and len(code) == 12:
            self._is_code_valid = True
            self.valid_icon_label.config(text="✔", fg="green")
        else:
            self._is_code_valid = False
            self.valid_icon_label.config(text="", fg="red") # Clear or show X

    def _verify_code_threaded(self):
        """
        Starts the verification process in a separate thread to keep the UI responsive.
        """
        # Disable button and show loading message immediately
        self.verify_button.config(state=tk.DISABLED)
        self.loading_label.config(text="Verifying...", fg="blue")

        # Start the actual verification in a new thread
        thread = threading.Thread(target=self._verify_code_logic)
        thread.start()

    def _verify_code_logic(self):
        """
        Contains the core verification logic (simulated delay and check).
        This runs in a separate thread.
        """
        if self._is_code_valid:
            time.sleep(2) # Simulate network delay

            entered_code = self.code_var.get()

            # Update UI on the main thread after delay
            self.master.after(0, self._process_verification_result, entered_code)
        else:
            # Update UI on the main thread if code is not valid
            self.master.after(0, self._show_message, '⚠️ Please enter 12 digits')
            self.master.after(0, self._reset_ui) # Reset UI immediately if invalid

    def _process_verification_result(self, entered_code):
        """
        Processes the result of the verification and updates the UI.
        This runs on the main Tkinter thread.
        """
        if entered_code == "123456789123":
            self._show_success_page()
        else:
            self._show_message('❌ Invalid Data')
            self._reset_ui() # Reset UI if invalid

    def _show_message(self, message):
        """
        Displays a message using a Tkinter messagebox.
        Args:
            message (str): The message to display.
        """
        messagebox.showinfo("Verification Status", message)

    def _reset_ui(self):
        """Resets the UI elements after verification."""
        self.verify_button.config(state=tk.NORMAL)
        self.loading_label.config(text="")

    def _show_success_page(self):
        """
        Creates and displays the success page.
        """
        self.master.withdraw() # Hide the main window

        success_window = tk.Toplevel(self.master)
        success_window.title("Verification Success")
        success_window.geometry("400x300")
        success_window.resizable(False, False)
        success_window.configure(bg="#66BB6A") # Green background
        success_window.transient(self.master) # Make it appear on top of main window
        success_window.grab_set() # Make it modal

        # Center the success window
        success_window.update_idletasks()
        width = success_window.winfo_width()
        height = success_window.winfo_height()
        x = (success_window.winfo_screenwidth() // 2) - (width // 2)
        y = (success_window.winfo_screenheight() // 2) - (height // 2)
        success_window.geometry(f'{width}x{height}+{x}+{y}')

        # Success Icon (using Unicode checkmark)
        success_icon = tk.Label(success_window,
                                text="✔",
                                font=("Arial", 100),
                                fg="white",
                                bg="#66BB6A")
        success_icon.pack(pady=(50, 20))

        # Success Message
        success_text = tk.Label(success_window,
                                text="Verified Successfully!",
                                font=("Arial", 26, "bold"),
                                fg="white",
                                bg="#66BB6A")
        success_text.pack()

        # Simulate animation and navigate after delay
        # Tkinter doesn't have built-in animation like Flutter.
        # We'll just have the window appear and then close after a delay.
        success_window.after(2000, lambda: self._navigate_to_home(success_window))

    def _navigate_to_home(self, success_window):
        """
        Closes the success window and simulates navigation to the home screen.
        Args:
            success_window: The success Toplevel window to close.
        """
        success_window.destroy()
        # In a real application, you would open your HomeScreen here.
        # For this example, we'll just show a message and close the main app.
        messagebox.showinfo("Navigation", "Navigating to Home Screen (App will close now).")
        self.master.destroy() # Close the main application window

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthCodeApp(root)
    root.mainloop()
