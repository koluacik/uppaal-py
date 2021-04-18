"""Benchmarks comparing NTA.to_file and NTA.flush_constraint_changes."""

import random
import timeit

from uppaalpy.classes.class_tests.random_changers import random_scenario

REPEAT = 5000




def random_scenario_without_specific_change_counts(nta_file, change_count):
    """Apply random changes."""
    # Partition change count into three.
    # ****|****|** etc.
    left, right = sorted(
        [random.randint(1, change_count), random.randint(1, change_count)]
    )
    insert = left
    remove = right - left
    update = change_count - right
    return random_scenario(nta_file, insert, remove, update)


def divide():
    """Print a line."""
    print()
    print(20 * "=")
    print()


def apply_random_scenario(nta_file, scenario, random_counts):
    """Benchmark a random case."""
    divide()
    print(
        "Applying random scenario of {}i/{}r/{}u on {}".format(*random_counts, nta_file)
    )
    nta = scenario(nta_file, *random_counts)

    acc_time = 0
    print("BENCHMARKING: nta.to_file (lxml): ", end="", flush=True)
    for _ in range(REPEAT):
        start = timeit.default_timer()
        nta.to_file("/tmp/out.xml")
        end = timeit.default_timer()
        acc_time += end - start
    print(acc_time)

    acc_time = 0
    print("BENCHMARKING: nta.flush_constraint_changes: ", end="", flush=True)
    for _ in range(REPEAT):
        start = timeit.default_timer()
        nta.flush_constraint_changes("/tmp/out.xml")
        end = timeit.default_timer()
        acc_time += end - start
    print(acc_time)


if __name__ == "__main__":
    small_nta = "benchmarks/ntas/small_nta.xml"
    big_nta = "benchmarks/ntas/big_nta.xml"

    divide()
    print("EXECUTING EACH SCENARIO %s TIMES." % (REPEAT))
    divide()
    print("SMALL NTA")

    apply_random_scenario(small_nta, random_scenario, (1, 0, 0))
    apply_random_scenario(small_nta, random_scenario, (0, 1, 0))
    apply_random_scenario(small_nta, random_scenario, (0, 0, 1))

    apply_random_scenario(small_nta, random_scenario, (1, 1, 0))
    apply_random_scenario(small_nta, random_scenario, (0, 2, 0))
    apply_random_scenario(small_nta, random_scenario, (2, 0, 0))

    apply_random_scenario(small_nta, random_scenario, (2, 1, 0))
    apply_random_scenario(small_nta, random_scenario, (0, 2, 1))
    apply_random_scenario(small_nta, random_scenario, (2, 1, 0))

    apply_random_scenario(small_nta, random_scenario, (2, 2, 0))
    apply_random_scenario(small_nta, random_scenario, (0, 3, 1))
    apply_random_scenario(small_nta, random_scenario, (4, 0, 0))

    apply_random_scenario(small_nta, random_scenario, (2, 2, 1))
    apply_random_scenario(small_nta, random_scenario, (1, 3, 1))
    apply_random_scenario(small_nta, random_scenario, (4, 1, 0))

    apply_random_scenario(small_nta, random_scenario, (2, 2, 2))
    apply_random_scenario(small_nta, random_scenario, (1, 3, 2))
    apply_random_scenario(small_nta, random_scenario, (4, 1, 1))

    apply_random_scenario(small_nta, random_scenario, (5, 0, 0))
    apply_random_scenario(small_nta, random_scenario, (4, 1, 0))
    apply_random_scenario(small_nta, random_scenario, (1, 2, 2))

    apply_random_scenario(small_nta, random_scenario, (2, 2, 2))
    apply_random_scenario(small_nta, random_scenario, (6, 0, 0))
    apply_random_scenario(small_nta, random_scenario, (1, 1, 4))

    apply_random_scenario(small_nta, random_scenario, (2, 2, 3))
    apply_random_scenario(small_nta, random_scenario, (6, 0, 1))
    apply_random_scenario(small_nta, random_scenario, (1, 2, 4))

    apply_random_scenario(small_nta, random_scenario, (3, 2, 3))
    apply_random_scenario(small_nta, random_scenario, (6, 1, 1))
    apply_random_scenario(small_nta, random_scenario, (2, 2, 4))

    apply_random_scenario(small_nta, random_scenario, (3, 3, 3))
    apply_random_scenario(small_nta, random_scenario, (6, 2, 1))
    apply_random_scenario(small_nta, random_scenario, (2, 3, 4))

    apply_random_scenario(small_nta, random_scenario, (4, 3, 3))
    apply_random_scenario(small_nta, random_scenario, (6, 2, 2))
    apply_random_scenario(small_nta, random_scenario, (2, 3, 5))

    divide()
    print("SMALL NTA")
    print("BIG NTA")

    apply_random_scenario(big_nta, random_scenario, (1, 0, 0))
    apply_random_scenario(big_nta, random_scenario, (0, 1, 0))
    apply_random_scenario(big_nta, random_scenario, (0, 0, 1))

    apply_random_scenario(big_nta, random_scenario, (1, 1, 0))
    apply_random_scenario(big_nta, random_scenario, (0, 2, 0))
    apply_random_scenario(big_nta, random_scenario, (2, 0, 0))

    apply_random_scenario(big_nta, random_scenario, (2, 1, 0))
    apply_random_scenario(big_nta, random_scenario, (0, 2, 1))
    apply_random_scenario(big_nta, random_scenario, (2, 1, 0))

    apply_random_scenario(big_nta, random_scenario, (2, 2, 0))
    apply_random_scenario(big_nta, random_scenario, (0, 3, 1))
    apply_random_scenario(big_nta, random_scenario, (4, 0, 0))

    apply_random_scenario(big_nta, random_scenario, (2, 2, 1))
    apply_random_scenario(big_nta, random_scenario, (1, 3, 1))
    apply_random_scenario(big_nta, random_scenario, (4, 1, 0))

    apply_random_scenario(big_nta, random_scenario, (2, 2, 2))
    apply_random_scenario(big_nta, random_scenario, (1, 3, 2))
    apply_random_scenario(big_nta, random_scenario, (4, 1, 1))

    apply_random_scenario(big_nta, random_scenario, (5, 0, 0))
    apply_random_scenario(big_nta, random_scenario, (4, 1, 0))
    apply_random_scenario(big_nta, random_scenario, (1, 2, 2))

    apply_random_scenario(big_nta, random_scenario, (2, 2, 2))
    apply_random_scenario(big_nta, random_scenario, (6, 0, 0))
    apply_random_scenario(big_nta, random_scenario, (1, 1, 4))

    apply_random_scenario(big_nta, random_scenario, (2, 2, 3))
    apply_random_scenario(big_nta, random_scenario, (6, 0, 1))
    apply_random_scenario(big_nta, random_scenario, (1, 2, 4))

    apply_random_scenario(big_nta, random_scenario, (3, 2, 3))
    apply_random_scenario(big_nta, random_scenario, (6, 1, 1))
    apply_random_scenario(big_nta, random_scenario, (2, 2, 4))

    apply_random_scenario(big_nta, random_scenario, (3, 3, 3))
    apply_random_scenario(big_nta, random_scenario, (6, 2, 1))
    apply_random_scenario(big_nta, random_scenario, (2, 3, 4))

    apply_random_scenario(big_nta, random_scenario, (4, 3, 3))
    apply_random_scenario(big_nta, random_scenario, (6, 2, 2))
    apply_random_scenario(big_nta, random_scenario, (2, 3, 5))
