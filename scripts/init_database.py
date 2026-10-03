from __future__ import annotations
from vantawave.db.config import load_database_config
from vantawave.db.init import initialize_database

def main():
    config = load_database_config()
    initialize_database()
    print("VantaWave database initialized")
    print(f"url: {config.url}")
    print(f"postgresql: {config.is_postgresql}")

if __name__ == "__main__":
    main()
