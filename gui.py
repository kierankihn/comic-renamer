import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

from renamer import rename_comics

def setup_logging(verbose: bool, log_text: tk.Text) -> None:
    """
    Set up logging level based on verbosity.
    """
    class TextHandler(logging.Handler):
        def __init__(self, text):
            logging.Handler.__init__(self)
            self.text = text

        def emit(self, record):
            msg = self.format(record)
            self.text.insert(tk.END, msg + '\n')
            self.text.yview(tk.END)  # Auto-scroll to the bottom

    logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s - %(message)s', level=logging.INFO if verbose else logging.WARN, handlers = [TextHandler(log_text)])

def main_gui():
    """
    Main function to execute the comic renaming process with GUI.
    """
    def browse_directory():
        folder_selected = filedialog.askdirectory()
        folder_path.set(folder_selected)

    def start_renaming():
        path = folder_path.get()
        format_str = format_entry.get()
        if not path:
            messagebox.showerror("Error", "Please select a directory.")
            return
        if not format_str:
            messagebox.showerror("Error", "Please enter a format.")
            return
        
        setup_logging(verbose_var, log_text)

        # Disable the start button to prevent multiple threads
        start_button.config(state=tk.DISABLED)

        # Start the renaming process in a separate thread
        threading.Thread(target=lambda: rename_comics(path, format_str, use_tw_press_var, progress_var, progress_bar, enable_start_button)).start()

    def enable_start_button():
        start_button.config(state=tk.NORMAL)

    root = tk.Tk()
    root.title("Comic Renamer")
    root.geometry("600x440")  # Set initial window size

    folder_path = tk.StringVar()
    format_str = tk.StringVar(value='{namecn} {author}')
    progress_var = tk.DoubleVar()
    verbose_var = tk.BooleanVar(value=False)
    use_tw_press_var = tk.BooleanVar(value=False)

    tk.Label(root, text="Directory:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
    tk.Entry(root, textvariable=folder_path, width=50).grid(row=0, column=1, padx=10, pady=10, sticky='ew')
    tk.Button(root, text="Browse", command=browse_directory).grid(row=0, column=2, padx=10, pady=10, sticky='e')

    tk.Label(root, text="Format:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
    format_entry = tk.Entry(root, textvariable=format_str, width=50)
    format_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')

    tk.Checkbutton(root, text="Show More Logs", variable=verbose_var).grid(row=2, column=0, padx=10, pady=10, sticky='w')
    tk.Checkbutton(root, text="Use Taiwan Press Info", variable=use_tw_press_var).grid(row=3, column=0, padx=10, pady=10, sticky='w')

    start_button = tk.Button(root, text="Start Renaming", command=start_renaming, width=15, height=1, anchor="center")
    start_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

    log_text = tk.Text(root, height=10, width=60)
    log_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

    # Make columns and rows expandable
    root.columnconfigure(1, weight=1)
    root.rowconfigure(4, weight=1)

    root.mainloop()

if __name__ == '__main__':
    main_gui()