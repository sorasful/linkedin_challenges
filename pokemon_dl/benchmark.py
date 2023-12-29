import asyncio
import os
import statistics
import time

os.environ["IS_BENCHMARKING"] = "1"

from pokemon_dl import pokemon


NB_ITERATIONS = 10


async def main() -> 0:
    times = []
    for i in range(NB_ITERATIONS):
        start = time.perf_counter()
        await pokemon.main()
        end = time.perf_counter()

        total_time = end - start

        times.append(total_time)

    print("Summary : ")
    print(f"{sum(times)/NB_ITERATIONS}s average of time for {NB_ITERATIONS} iterations")
    print(f"Standard deviation : {statistics.stdev(times)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
