"""Benchmarks comparing NTA.to_file and NTA.flush_constraint_changes."""

import timeit

import uppaalpy

REPEAT = 2500

small_nta = "benchmarks/ntas/small_nta.xml"


def scenario1():
    """Scenario1: Insert a constraint to l0 in first template."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    location = nta.templates[0].graph._named_locations["l0"]
    new_constraint = uppaalpy.SCConstraint(["x", "y"], "<", 15)
    nta.change_location_constraint(
        location, operation="insert", simple_constraint=new_constraint
    )
    return nta


def scenario2():
    """Scenario2: Remove a constraint from l0 in first template."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    location = nta.templates[0].graph._named_locations["l0"]
    constraint = location.invariant.constraints[0]
    nta.change_location_constraint(
        location, operation="remove", simple_constraint=constraint
    )
    return nta


def scenario3():
    """Scenario3: Update a constraint in l0 in first template."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    location = nta.templates[0].graph._named_locations["l0"]
    constraint = location.invariant.constraints[0]
    nta.change_location_constraint(
        location, operation="update", simple_constraint=constraint, threshold_delta=15
    )
    return nta


def scenario4():
    """Scenario4: Insert a guard in the first template."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    # The transition without guard between l1 and l2.
    transition = nta.templates[0].graph._transitions[1]
    new_constraint = uppaalpy.SCConstraint(["x", "y"], "<", 15)
    nta.change_transition_constraint(
        transition, operation="insert", simple_constraint=new_constraint
    )
    return nta


def scenario5():
    """Scenario5: Increment one invariant, create one guard and increment it."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    location = nta.templates[0].graph._named_locations["l0"]

    constraint = location.invariant.constraints[0]
    nta.change_location_constraint(
        location, operation="update", simple_constraint=constraint, threshold_delta=15
    )

    transition = nta.templates[0].graph._transitions[1]
    new_constraint = uppaalpy.SCConstraint(["x", "y"], "<", 15)
    nta.change_transition_constraint(
        transition, operation="insert", simple_constraint=new_constraint
    )

    nta.change_transition_constraint(
        transition,
        operation="update",
        simple_constraint=new_constraint,
        threshold_function=(lambda x: x + 3),
    )

    return nta


def scenario6():
    """Scenario6: Repeatedly insert, change, and remove a guard 5 times."""
    nta = uppaalpy.NTA.from_xml(small_nta)
    # The transition without guard between l1 and l2.
    transition = nta.templates[0].graph._transitions[1]
    new_constraint = uppaalpy.SCConstraint(["x", "y"], "<", 15)

    for _ in range(5):
        nta.change_transition_constraint(
            transition, operation="insert", simple_constraint=new_constraint
        )
        nta.change_transition_constraint(
            transition,
            operation="update",
            simple_constraint=new_constraint,
            threshold_delta=1,
        )
        nta.change_transition_constraint(
            transition,
            operation="remove",
            simple_constraint=transition.guard.constraints[0],
        )

    return nta


def divide():
    """Print a line."""
    print()
    # print(os.get_terminal_size().columns * "=")
    print(40 * "=")
    print()


def apply_scenario(scenario):
    """Given a scenario function, print its docstring and execute it."""
    divide()
    print(scenario.__doc__)

    nta = scenario()

    acc_time = 0
    print("BENCHMARKING: nta.to_file (lxml): ", end="", flush=True)
    nta = scenario()
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
    divide()
    print("EXECUTING EACH SCENARIO %s TIMES." % (REPEAT))

    scenarios = [scenario1, scenario2, scenario3, scenario4, scenario5, scenario6]
    # scenarios = [scenario5]

    for s in scenarios:
        apply_scenario(s)
    divide()
