import os
import time
import random
import threading
import requests
from collections import defaultdict

TARGET     = os.environ.get("TARGET_URL",  "http://caddy:80")
WORKERS    = int(os.environ.get("WORKERS",    10))
DELAY_MIN  = float(os.environ.get("DELAY_MIN", 5))   # minimale Wartezeit in Sekunden
DELAY_MAX  = float(os.environ.get("DELAY_MAX", 9))   # maximale Wartezeit in Sekunden

stats = defaultdict(int)
errors = 0
lock = threading.Lock()


def worker(worker_id: int):
    global errors
    session = requests.Session()
    while True:
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        time.sleep(delay)
        try:
            t0 = time.time()
            resp = session.get(TARGET, timeout=5)
            elapsed_ms = (time.time() - t0) * 1000
            data = resp.json()
            server   = data.get("server",           "unbekannt")
            handled  = data.get("requests_handled", "?")
            uhrzeit  = time.strftime("%H:%M:%S")
            with lock:
                stats[server] += 1
            print(f"\n{uhrzeit}  [Worker {worker_id}]  {server}  |  {resp.status_code}  |  {elapsed_ms:.0f} ms  |  Server-Zaehler: {handled}")
        except Exception as exc:
            with lock:
                errors += 1
            uhrzeit = time.strftime("%H:%M:%S")
            print(f"\n{uhrzeit}  [Worker {worker_id}]  FEHLER: {exc}")


def stats_printer():
    while True:
        time.sleep(30)
        with lock:
            total = sum(stats.values())
            print("\n" + "=" * 50)
            print(f"  STATISTIK  (Gesamt: {total} Anfragen, Fehler: {errors})")
            print("=" * 50)
            for server in sorted(stats):
                count = stats[server]
                pct = count / total * 100 if total > 0 else 0
                bar = "#" * int(pct / 2)
                print(f"  {server:<14} {count:>5}x  ({pct:5.1f}%)  {bar}")
            print("=" * 50 + "\n")


print("Stress-Generator startet")
print(f"  Ziel    : {TARGET}")
print(f"  Workers : {WORKERS} Threads")
print(f"  Delay   : {DELAY_MIN}–{DELAY_MAX}s (zufaellig pro Anfrage)")
print("  Statistik alle 30s\n")

threads = [threading.Thread(target=worker, args=(i + 1,), daemon=True) for i in range(WORKERS)]
threads.append(threading.Thread(target=stats_printer, daemon=True))
for t in threads:
    t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStress-Generator gestoppt.")
