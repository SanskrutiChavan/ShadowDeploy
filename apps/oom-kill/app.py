import time

print("=== Analytics Service Starting ===", flush=True)
print("Loading data pipeline...", flush=True)

leak = []
mb = 0

while True:
    leak.append("x" * 1024 * 1024)  # add 1 MB every 0.5s
    mb += 1
    print(f"Memory used: {mb} MB", flush=True)
    time.sleep(0.5)