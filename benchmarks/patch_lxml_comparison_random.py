"""Benchmarks comparing NTA.to_file and NTA.flush_constraint_changes."""

import random
import timeit

import uppaalpy
from uppaalpy.classes.simplethings import SimpleConstraint

REPEAT = 5000


def select_random_transition(nta, nonempty=False):
    """Select a random transition.

    If nonempty is True, keep selecting until one with constraints is found.
    """
    while True:
        t = random.choice(nta.templates)
        trans = random.choice(t.graph._transitions)
        if not (nonempty and trans.guard is None):
            break

    return trans


def select_random_location(nta, nonempty=False):
    """Select a random location.

    If nonempty is True, keep selecting until one with constraints is found.
    """
    while True:
        t = random.choice(nta.templates)
        locs = t.graph.get_nodes()
        loc = random.choice(locs)
        if not (nonempty and loc.invariant is None):
            break

    return loc


def make_random_insert(nta):
    """Insert a random constraint to a random transition or location."""
    change_transition = random.choice([True, False])

    if change_transition:
        trans = select_random_transition(nta)
        nta.change_transition_constraint(
            trans,
            operation="insert",
            simple_constraint=SimpleConstraint(
                ["x"], random.choice(["<", ">"]), random.randint(1, 100)
            ),
        )

    else:
        location = select_random_location(nta)
        nta.change_location_constraint(
            location,
            operation="insert",
            simple_constraint=SimpleConstraint(
                ["x"], random.choice(["<", ">"]), random.randint(1, 100)
            ),
        )


def make_random_remove(nta):
    """Remove a random constraint from a random transition or location."""
    change_transition = random.choice([True, False])

    if change_transition:
        trans = select_random_transition(nta, nonempty=True)
        nta.change_transition_constraint(
            trans,
            operation="remove",
            simple_constraint=random.choice(trans.guard.constraints),
        )

    else:
        location = select_random_location(nta, nonempty=True)
        nta.change_location_constraint(
            location,
            operation="remove",
            simple_constraint=random.choice(location.invariant.constraints),
        )


def make_random_update(nta):
    """Update a random constraint from a random transition or location."""
    change_transition = random.choice([True, False])

    if change_transition:
        trans = select_random_transition(nta, nonempty=True)
        nta.change_transition_constraint(
            trans,
            operation="update",
            simple_constraint=random.choice(trans.guard.constraints),
            threshold_delta=random.randint(1, 10),
        )

    else:
        location = select_random_location(nta, nonempty=True)
        nta.change_location_constraint(
            location,
            operation="update",
            simple_constraint=random.choice(location.invariant.constraints),
            threshold_delta=random.randint(1, 10),
        )


def random_scenario(nta_file, insert_count, remove_count, update_count):
    """Apply random changes for each given change type."""
    nta = uppaalpy.NTA.from_xml(nta_file)
    for _ in range(insert_count):
        make_random_insert(nta)

    for _ in range(remove_count):
        make_random_remove(nta)

    for _ in range(update_count):
        make_random_update(nta)

    return nta


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
        nta.to_file("/tmp/out.xml", pretty=True)
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
