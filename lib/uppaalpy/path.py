"""Functions for path analysis."""
from ortools.linear_solver import pywraplp

EPS = 2 ** (-10)


def path_exists(path):
    """Return true if each edge is from previous location to next location."""
    for i in range(1, len(path) - 1, 2):
        if path[i - 1].id != path[i].source or path[i + 1].id != path[i].target:
            return False
    return True


def find_used_clocks(path):
    """Return the list of clocks that will be checked in path."""
    res = []
    for element in path:
        constraints = element.get_constraints()
        for c in constraints:
            for clock in c.clocks:
                if clock not in res:
                    res.append(clock)
    res.sort()
    return res


def convert_to_path(template, lst):
    """Given a template and a list return a list of node and edges.

    Args:
        template: Template name.
        lst: Alternating list of location name strings and edge id's.
    Returns:
        An alternating list of location and transition objects.

    Example: extract_path(temp, ["l0", 1, "l2", 3, "l2"])
    returns an alternating list of location and edge objects.
    Locations are denoted with strings denoting their name fields.
    Edges are enumerated with zero-indexed integers according to their
    order in the xml file.
    This function makes use of nta.locations dictionary, hence it is assumed
    that each location in the graph is uniquely identified by their name field.
    """
    path = []
    for i, rep in enumerate(lst):
        if i % 2:
            path.append(template.graph._transitions[rep])
        else:
            path.append(template.graph._named_locations[rep])
    return path


def path_realizable(path, validate_path=False, add_epsilon=False):
    """Given a path, construct an LP and return results.

    Args:
        path: List of alternating location and transitions.
        validate_path: Check whether each transition is actually between
            the previous location and the next location.
        add_epsilon: Add epsilon to constraints with operators '<' and '>'.
            This is useful for invalidating solutions that would be otherwise
            correct with operators '<=' or '>='.
    Returns:
        A tuple of a bool and a witness list of delays for each location.
    """
    if validate_path and not path_exists(path):
        return False, []
    length_of_path = len(path) // 2

    clocks = find_used_clocks(path)

    A = []
    B = []

    clock_to_delay = dict()

    for x in clocks:
        clock_to_delay[x] = [0]

    for i in range(0, len(path) - 1, 2):
        # Source location
        l = path[i]
        if l.invariant is not None:
            for c in l.invariant.constraints:
                a, b = compute_constraint(
                    clock_to_delay, c, length_of_path, add_epsilon
                )
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Transition
        t = path[i + 1]
        if t.guard is not None:
            for c in t.guard.constraints:
                a, b = compute_constraint(
                    clock_to_delay, c, length_of_path, add_epsilon
                )
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Resets
        resets_in_transition = get_resets(t, clock_to_delay.keys())
        for x in resets_in_transition:
            clock_to_delay[x] = []

        # Target location
        l = path[i + 2]
        if l.invariant is not None:
            for c in l.invariant.constraints:
                a, b = compute_constraint(
                    clock_to_delay, c, length_of_path, add_epsilon
                )
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Add delays
        for x in clocks:
            clock_to_delay[x].append(i // 2 + 1)

    solver = pywraplp.Solver("", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    x = {}

    for j in range(length_of_path):
        x[j] = solver.NumVar(0, solver.infinity(), "x[%s]" % j)

    for i in range(len(A)):
        constraint = solver.RowConstraint(-solver.infinity(), B[i], "")
        for j in range(length_of_path):
            constraint.SetCoefficient(x[j], A[i][j])

    status = solver.Solve()

    delays = []

    if status == solver.OPTIMAL:
        for i in range(length_of_path):
            delays.append(x[i].solution_value())
        return True, delays

    if status == solver.INFEASIBLE:
        return False, []


def get_resets(transition, clocks):
    """Find clocks to be reset upon taking the transition.

    Args:
        transition: A transition object.
        clocks: List of used clocks in the analysis.

    Returns:
        list of clocks to be reset.
    """
    if transition.assignment is None:
        return []
    a_strings = [s.strip() for s in transition.assignment.value.split(",")]
    resets = []
    for assignment in a_strings:
        tokens = [word.strip().rstrip() for word in assignment.split("=")]
        if len(tokens) == 2 and tokens[1] == "0" and tokens[0] in clocks:
            resets.append(tokens[0])
    return resets


def compute_constraint(
    clock_to_delay, simple_constraint, variable_count, add_epsilon=False
):
    """Construct a row of the Linear Program.

    Args:
        clock_to_delay: Dictionary of list of ints. clock_to_delay['x'] gives
            a list of delay variables for the locations visited since the last
            reset of clock 'x'.
        variable_count: Int for determining the row size.
        add_epsilon: Whether to treat '<=' as '<' by adding an epsilon value to
            the threshold.
    """
    A_row = [[0 for _ in range(variable_count)]]
    for delay_var in clock_to_delay[simple_constraint.clocks[0]]:
        A_row[0][delay_var] = 1

    if len(simple_constraint.clocks) == 2:  # clock difference
        for delay_var in clock_to_delay[simple_constraint.clocks[1]]:
            A_row[0][delay_var] -= 1

    B_row = [simple_constraint.threshold]
    if simple_constraint.operator == ">":
        A_row[0] = [x * -1 for x in A_row[0]]
        B_row[0] = -1 * B_row[0]

    if add_epsilon and simple_constraint.equality == False:  # Inequality: Add epsilon.
        B_row[0] -= EPS

    if simple_constraint.operator == "=":
        A_row.append([x * -1 for x in A_row[0]])
        B_row.append(-B_row[0])

    return A_row, B_row


if __name__ == "__main__":
    from uppaalpy.classes import NTA

    temp = NTA.from_xml("examples/generator/test5_6_2.xml").templates[0]
    mypath = convert_to_path(temp, ["l0", 0, "l2", 1, "l3", 2, "l4"])
