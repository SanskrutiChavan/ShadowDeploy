import time, random, sys

print("=== Order Service Starting ===", flush=True)
print("Connecting to services...", flush=True)
time.sleep(random.randint(3, 8))

# Simulate random unhandled exception

errors = [
"ConnectionRefusedError: Redis connection refused on port 6379",
"RuntimeError: Segmentation fault in native module",
"MemoryError: Cannot allocate memory for request buffer",
"OSError: Too many open file descriptors",
]

print(f"CRITICAL: {random.choice(errors)}", flush=True)
print("Stack trace: ...", flush=True)
sys.exit(1)
