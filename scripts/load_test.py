"""SteadyVox Concurrency & Load Benchmark.

Simulates 1, 5, and 10 concurrent screening requests.
Measures p50, p95, p99 latency, throughput (req/s), and error rate against SLO (< 2000 ms).
"""

import asyncio
import time
import sys
from pathlib import Path
import numpy as np
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, "/home/saravana/SteadyVox")
from backend.app.main import app

SAMPLE_WAV = "/home/saravana/SteadyVox/storage/audio/recordings/43bd02f7-f894-49d4-933a-60db8e914dfa.wav"


async def worker(client: AsyncClient, wav_bytes: bytes, latencies: list, errors: list):
    t0 = time.perf_counter()
    try:
        files = {"file": ("bench.wav", wav_bytes, "audio/wav")}
        data = {"patient_identifier": "LOAD-BENCH", "consent_given": "false"}
        resp = await client.post("/api/v1/screen", files=files, data=data)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if resp.status_code == 201:
            latencies.append(elapsed_ms)
        else:
            errors.append(f"HTTP {resp.status_code}")
    except Exception as e:
        errors.append(str(e))


async def run_load_level(concurrent_users: int, total_requests: int, wav_bytes: bytes):
    print(f"\n==========================================")
    print(f"LOAD TEST: {concurrent_users} Concurrent Users ({total_requests} requests total)")
    print(f"==========================================")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        # Exclude Warm-up
        files = {"file": ("warmup.wav", wav_bytes, "audio/wav")}
        await client.post("/api/v1/screen", files=files)

        latencies = []
        errors = []

        t_start = time.perf_counter()
        
        # Batch tasks into concurrent chunks
        tasks = []
        for _ in range(total_requests):
            tasks.append(worker(client, wav_bytes, latencies, errors))
            if len(tasks) >= concurrent_users:
                await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)

        t_total = time.perf_counter() - t_start
        throughput = len(latencies) / t_total if t_total > 0 else 0

        p50 = np.percentile(latencies, 50) if latencies else 0
        p95 = np.percentile(latencies, 95) if latencies else 0
        p99 = np.percentile(latencies, 99) if latencies else 0
        err_rate = (len(errors) / total_requests) * 100.0

        slo_met = p95 <= 2000.0

        print(f"Throughput: {throughput:.2f} req/s")
        print(f"Success Count: {len(latencies)} / {total_requests}")
        print(f"Error Rate: {err_rate:.1f}%")
        print(f"Latency p50: {p50:.2f} ms")
        print(f"Latency p95: {p95:.2f} ms")
        print(f"Latency p99: {p99:.2f} ms")
        print(f"Latency SLO (< 2000 ms): {'MET (PASS)' if slo_met else 'VIOLATED (FAIL)'}")

        return {
            "concurrency": concurrent_users,
            "throughput": round(throughput, 2),
            "p50": round(p50, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
            "error_rate": round(err_rate, 2),
            "slo_met": slo_met,
        }


async def main():
    with open(SAMPLE_WAV, "rb") as f:
        wav_bytes = f.read()

    results = []
    # 1 Concurrent User (10 requests)
    results.append(await run_load_level(1, 10, wav_bytes))
    # 5 Concurrent Users (15 requests)
    results.append(await run_load_level(5, 15, wav_bytes))
    # 10 Concurrent Users (20 requests)
    results.append(await run_load_level(10, 20, wav_bytes))

    print("\n--- SUMMARY REPORT ---")
    for r in results:
        print(f"Users: {r['concurrency']} | Throughput: {r['throughput']} req/s | p95: {r['p95']} ms | SLO Met: {r['slo_met']}")

if __name__ == "__main__":
    asyncio.run(main())
