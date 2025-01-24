# SQLite Database Decryptor

A powerful GUI tool for decrypting and extracting data from SQLite databases, with special support for Chrome's encrypted databases.

## Features

- 🔒 Automatic Chrome encryption key detection and decryption
- 📊 Handles all SQLite database types
- 🔄 Special handling for sync metadata and binary data
- 💾 Exports all tables to JSON format
- 📝 Real-time progress tracking
- 🎯 Simple one-click operation

## Installation

1. Download the latest release from the `dist` folder
2. Run `SQLite Decryptor.exe`
3. No installation required - it's portable!

## Usage

1. Launch the application
2. Click "Browse" to select your SQLite database file
3. The decryption process will start automatically
4. Find your decrypted data in the `dump_[database]_[timestamp]` folder

## Supported Data Types

- ✅ Chrome encrypted data (passwords, cookies, etc.)
- ✅ Binary data (automatically converted to base64)
- ✅ Timestamps (automatically converted to ISO format)
- ✅ Text data (UTF-8 with fallback encoding)
- ✅ Sync metadata (preserved in base64 format)

## Development

### Requirements
- Python 3.8+
- Required packages:
  ```
  pycryptodome
  pywin32
  keyring
  ```

### Project Structure
```
SQLite-Decryptor/
├── src/
│   ├── __init__.py
│   ├── gui.py              # Main GUI implementation
│   ├── decryptor.py        # Core decryption logic
│   └── utils.py            # Utility functions
├── dist/
│   └── SQLite Decryptor.exe
├── build/                  # Build files
├── tests/                  # Test files
├── requirements.txt        # Project dependencies
├── README.md              # This file
└── sqlite_decrypt_gui.spec # PyInstaller spec file
```

### Building from Source

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build executable:
   ```bash
   pyinstaller sqlite_decrypt_gui.spec
   ```

## License

MIT License - Feel free to use and modify!
