"""Helpers for making random changes on NTA."""
#TODO: Reimplement this module

import random
from uppaalpy import NTA
from uppaalpy.classes.expr import ClockConstraintExpression



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
    ctx = nta.context

    if change_transition:
        trans = select_random_transition(nta)
        nta.change_transition_constraint(
            trans,
            operation="insert",
            simple_constraint=ClockConstraintExpression(
                "c" + random.choice(["<", ">"]) + str(random.randint(1, 100)), ctx
            ),
        )

    else:
        location = select_random_location(nta)
        nta.change_location_constraint(
            location,
            operation="insert",
            simple_constraint=SCConstraint(
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
    nta = NTA.from_xml(nta_file)
    for _ in range(insert_count):
        make_random_insert(nta)

    for _ in range(remove_count):
        make_random_remove(nta)

    for _ in range(update_count):
        make_random_update(nta)

    return nta
