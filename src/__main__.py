import tkinter as tk
from src.gui import SQLiteDecryptorGUI

def main():
    root = tk.Tk()
    app = SQLiteDecryptorGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
