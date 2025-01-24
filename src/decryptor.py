import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import keyring
from src.utils import convert_timestamp, safe_decode, is_sync_metadata

class SQLiteDecryptor:
    def __init__(self, callback=None):
        """Initialize decryptor with optional callback for progress updates."""
        self.callback = callback or (lambda x: None)
        self.key = None

    def get_chrome_encryption_key(self):
        """Retrieve Chrome's encryption key."""
        try:
            if os.name == 'nt':
                local_state_path = os.path.join(
                    os.environ['LOCALAPPDATA'],
                    'Google', 'Chrome', 'User Data', 'Local State'
                )
                with open(local_state_path, 'r', encoding='utf-8') as f:
                    local_state = json.load(f)
                encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
                encrypted_key = encrypted_key[5:]  # Remove DPAPI prefix
                return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            elif os.name == 'posix':
                service = 'Chrome Safe Storage'
                username = 'Chrome'
                return keyring.get_password(service, username).encode('utf-8')
        except Exception as e:
            self.callback(f"Warning: Could not get Chrome encryption key: {e}")
        return None

    def decrypt_value(self, value):
        """Decrypt a single value using Chrome's encryption."""
        try:
            if not isinstance(value, (bytes, bytearray)) or not self.key:
                return value

            if len(value) > 15:
                iv = value[3:15]
                payload = value[15:]
                cipher = AES.new(self.key, AES.MODE_GCM, iv)
                decrypted = cipher.decrypt(payload)
                return safe_decode(decrypted[:-16])
            return safe_decode(value)
        except Exception:
            return safe_decode(value)

    def process_value(self, value, col_type=None):
        """Process a value based on its type and content."""
        if isinstance(value, (bytes, bytearray)):
            if is_sync_metadata(value):
                return base64.b64encode(value).decode('utf-8')
            return self.decrypt_value(value)
        elif isinstance(value, (int, float)):
            return convert_timestamp(value)
        elif isinstance(value, str):
            return value
        return str(value)

    def decrypt_database(self, db_path, output_dir):
        """Decrypt an entire SQLite database."""
        self.key = self.get_chrome_encryption_key()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        total_tables = len(tables)
        successful_tables = 0

        try:
            for i, (table_name,) in enumerate(tables, 1):
                self.callback(f"\nProcessing table: {table_name}")
                
                try:
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    column_types = [col[2].lower() for col in columns]

                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total_rows = cursor.fetchone()[0]
                    self.callback(f"Found {total_rows} rows")

                    # Process rows
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    table_data = []
                    for row_num, row in enumerate(rows, 1):
                        row_dict = {}
                        for j, value in enumerate(row):
                            col_type = column_types[j]
                            processed_value = self.process_value(value, col_type)
                            row_dict[column_names[j]] = processed_value
                        table_data.append(row_dict)
                        
                        if row_num % 100 == 0:
                            self.callback(f"Processed {row_num}/{total_rows} rows")

                    # Save to JSON
                    output_file = os.path.join(output_dir, f"{table_name}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(table_data, f, indent=2, ensure_ascii=False)

                    self.callback(f"✓ Successfully saved {len(table_data)} rows to {table_name}.json")
                    successful_tables += 1

                except Exception as e:
                    self.callback(f"❌ Error processing table {table_name}: {str(e)}")
                    self.callback("Continuing with next table...")

                # Return progress percentage
                yield (i / total_tables) * 100

        finally:
            cursor.close()
            conn.close()
