import os, sys, time

print("=== Payment Service Starting ===", flush=True)
time.sleep(2)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
API_KEY = os.environ.get("API_KEY")

if not DB_HOST:
    print("FATAL ERROR: DB_HOST environment variable is not set!", flush=True)
    print("Cannot connect to database. Exiting.", flush=True)
    sys.exit(1)

if not API_KEY:
    print("FATAL ERROR: API_KEY environment variable is not set!", flush=True)
    sys.exit(1)

print(f"Connected to DB at {DB_HOST}:{DB_PORT}", flush=True)
print("Service running...", flush=True)