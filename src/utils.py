import os
import base64
from datetime import datetime, timezone

def get_output_directory(db_path):
    """Create and return output directory path based on database name and timestamp."""
    db_name = os.path.splitext(os.path.basename(db_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"dump_{db_name}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def convert_timestamp(value):
    """Convert various timestamp formats to ISO format."""
    try:
        if value > 11644473600000000:  # Windows FILETIME epoch
            dt = datetime.fromtimestamp((value - 11644473600000000) / 1000000, timezone.utc)
            return dt.isoformat()
        elif value > 1000000000000:  # Unix timestamp in milliseconds
            dt = datetime.fromtimestamp(value / 1000, timezone.utc)
            return dt.isoformat()
        elif value > 1000000000:  # Unix timestamp in seconds
            dt = datetime.fromtimestamp(value, timezone.utc)
            return dt.isoformat()
        return value
    except:
        return value

def safe_decode(value, encoding='utf-8'):
    """Safely decode binary data with fallback to base64."""
    try:
        return value.decode(encoding, errors='ignore')
    except:
        try:
            return base64.b64encode(value).decode('utf-8')
        except:
            return value.hex()

def is_sync_metadata(value):
    """Check if the binary data is sync metadata."""
    return isinstance(value, (bytes, bytearray)) and (
        value.startswith(b'v10') or value.startswith(b'\nA')
    )
