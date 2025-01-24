import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from src.decryptor import SQLiteDecryptor
from src.utils import get_output_directory

class SQLiteDecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Database Decryptor")
        self.root.geometry("600x400")
        
        # Set style
        style = ttk.Style()
        style.configure('Custom.TButton', padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        self.file_frame = ttk.LabelFrame(main_frame, text="Database File", padding="5")
        self.file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path = tk.StringVar()
        self.file_path.trace_add('write', self.on_file_path_change)
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=0, padx=5)
        
        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self.browse_file, style='Custom.TButton')
        self.browse_button.grid(row=0, column=1, padx=5)
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        self.progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Status text
        self.status_text = tk.Text(main_frame, height=15, width=70, wrap=tk.WORD)
        self.status_text.grid(row=2, column=0, columnspan=2, pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.status_text['yscrollcommand'] = scrollbar.set
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.file_frame.columnconfigure(0, weight=1)
        self.progress_frame.columnconfigure(0, weight=1)

    def update_status(self, message):
        """Update status text with new message."""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def browse_file(self):
        """Open file browser dialog."""
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("All Files", "*.*")]
        )
        if filename:
            self.browse_button.config(state=tk.DISABLED)
            self.file_path.set(filename)

    def on_file_path_change(self, *args):
        """Handle file path changes."""
        if self.file_path.get() and os.path.exists(self.file_path.get()):
            self.update_status("File selected: " + self.file_path.get())
            self.start_decryption()

    def start_decryption(self):
        """Start the decryption process in a separate thread."""
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a database file first!")
            return
            
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.decrypt_database)
        thread.daemon = True
        thread.start()

    def decrypt_database(self):
        """Run the decryption process."""
        try:
            db_path = self.file_path.get()
            output_dir = get_output_directory(db_path)
            self.update_status(f"Created output directory: {output_dir}")

            decryptor = SQLiteDecryptor(callback=self.update_status)
            
            # Process the database and collect statistics
            successful_tables = 0
            total_tables = 0
            
            # Process each table and update progress
            for progress in decryptor.decrypt_database(db_path, output_dir):
                self.progress_var.set(progress)
                total_tables = int(progress * 100 / 100)  # Convert percentage back to count
            
            # Count successful tables from the output directory
            successful_tables = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
            
            # Show completion message
            self.update_status(f"\n=== Decryption Summary ===")
            self.update_status(f"Total tables processed: {total_tables}")
            self.update_status(f"Successfully processed: {successful_tables}")
            self.update_status(f"Failed tables: {total_tables - successful_tables}")
            self.update_status(f"Output directory: {output_dir}")
            
            if successful_tables > 0:
                messagebox.showinfo("Success", 
                    f"Successfully processed {successful_tables} tables.\n"
                    f"Data has been saved to {output_dir}")
            else:
                messagebox.showerror("Error", "Failed to process any tables successfully.")

        except Exception as e:
            self.update_status(f"Critical Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.browse_button.config(state=tk.NORMAL)
            self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = SQLiteDecryptorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
