"""Functions for path analysis."""
from ortools.linear_solver import pywraplp
from itertools import product

from uppaalpy.classes.expr import ClockConstraintExpression

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
            if not isinstance(c, ClockConstraintExpression):
                continue
            for clock in c.clocks:
                if clock not in res:
                    res.append(clock)
    res.sort()
    return res


def convert_to_path(template, lst):
    """Given a template and a list return a list of node and edges.

    Args:
        template: Template object.
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

    See: path_realizable_with_initial_valuation from this module.
    """
    return path_realizable_with_initial_valuation(path, validate_path, add_epsilon)


def path_realizable_with_initial_valuation(
    path, validate_path=False, add_epsilon=False, icv_constants=None, clocks=None
):
    """Given a path, construct an LP and return results.

    Args:
        path: List of alternating location and transitions.
        validate_path: Check whether each transition is actually between
            the previous location and the next location.
        add_epsilon: Add epsilon to constraints with operators '<' and '>'.
            This is useful for invalidating solutions that would be otherwise
            correct with operators '<=' or '>='.
        icv_constants: Dict for the initial valuation of the clocks at the first
            location of the path.  If left as None, all initial clock valuations
            will be assumed to be 0.  Otherwise clock valuations with provided
            clock names as keys are initially the value corresponding to the clock
            name. Clock valuations omitted will be constrained with "c >= 0".
        clocks: List of clock name strings. If None, find_used_clocks function will be
            used to determine the used clocks by iterating the path.
    Returns:
        A tuple of a bool and a witness list of delays for each location.
    """
    # Strategy:
    #
    # If icv is None:
    #       variable count <- length(path)
    #       construct lp  -- each var corresponds to time spent on a location
    #
    # Otherwise:
    #       variable count <- clock count + length(path)
    #       construct lp with:
    #           Consider a clock val variable for each clock.
    #           Prepend each clock_to_delay[clock] with a corresponding icv var.
    #           Forall clocks: if initial clock value is specified:
    #               Constrain clock.

    # Check whether the path exists (not necessarily realizable).
    if validate_path and not path_exists(path):
        return False, []

    # We will construct the LP using these.
    # Each row in A correspond to a sequence of coefficients
    # ai1, ai2, ai3... ain such that ai1 * var1 + ai2 * var2 ... <= bi.
    # Matrix A and vector B will be populated by the compute_constraint
    # procedure.
    A = []
    B = []

    # Find clock names.
    if clocks == None:
        clocks = find_used_clocks(path)

    clock_to_delay = dict()

    delay_var_count = len(path) // 2
    var_count = delay_var_count  # var_count can be updated depending on icv.
    delay_var_offset = 0

    # Are icv (initial clock valuations) >= 0, == 0, or == some other value?

    if icv_constants is not None:
        # Initial clock valuations are not 0. Add a icv var to the LP for each
        # clock. For the function parameter icv, if icv_constants[clock_name] exists,
        # constrain that icv with icv <= icv_constants[clock_name]
        # and -icv <= -icv_constants[clock_name] (icv == icv_constants[clock_name].

        icv_var_count = len(clocks)
        var_count = delay_var_count + icv_var_count
        delay_var_offset = icv_var_count

        for i, c in enumerate(clocks):
            a = [[0] * var_count]
            b = [0]
            a[0][i] = -1  # Since (-var in -inf, 0) <=> (var in 0, inf)
            A.append(a[0])
            B.append(b[0])
            try:
                clock_to_delay[c] = [i, delay_var_offset]
                icv_c = icv_constants[c]
                b[0] = icv_c  # c in -var <= -c
                b.append(-icv_c)  # c in var <= c
                a.append([-var for var in a[0]])
                A.append(a[1])
                B.append(b[1])
            except:
                pass

        for i, c in enumerate(clocks):
            clock_to_delay[c] = [i, delay_var_offset]

    else:
        # Initial clock valuations are all 0. No need to consider icv vars.
        # delay_var_offset is 0.
        for c in clocks:
            clock_to_delay[c] = [0]

    # Generate LP coefficients for each constraint.
    for i in range(0, len(path) - 1, 2):
        # Source location
        l = path[i]
        if l.invariant is not None:
            for c in l.invariant.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(clock_to_delay, c, var_count, add_epsilon)
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Transition
        t = path[i + 1]
        if t.guard is not None:
            for c in t.guard.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(clock_to_delay, c, var_count, add_epsilon)
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Resets
        # resets_in_transition = get_resets(t, clock_to_delay.keys())
        resets_in_transition = []
        if t.assignment is not None:
            resets_in_transition = t.assignment.get_resets()
        for c in resets_in_transition:
            clock_to_delay[c] = []

        # Target location
        l = path[i + 2]
        if l.invariant is not None:
            for c in l.invariant.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(clock_to_delay, c, var_count, add_epsilon)
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Add delays, consider delay_var_offset.
        for c in clocks:
            clock_to_delay[c].append(i // 2 + 1 + delay_var_offset)

    solver = pywraplp.Solver("", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    c = {}

    for j in range(var_count):
        c[j] = solver.NumVar(0, solver.infinity(), "x[%s]" % j)

    for i in range(len(A)):
        constraint = solver.RowConstraint(-solver.infinity(), B[i], "")
        for j in range(var_count):
            constraint.SetCoefficient(c[j], A[i][j])

    status = solver.Solve()

    delays = []

    if status == solver.OPTIMAL:
        for i in range(var_count):
            delays.append(c[i].solution_value())
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
    clock_to_delay, clock_constraint_expr, variable_count, add_epsilon=False
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
    for delay_var in clock_to_delay[clock_constraint_expr.clocks[0]]:
        A_row[0][delay_var] = 1

    if len(clock_constraint_expr.clocks) == 2:  # clock difference
        for delay_var in clock_to_delay[clock_constraint_expr.clocks[1]]:
            A_row[0][delay_var] -= 1

    # TODO: get value from context
    B_row = [int(clock_constraint_expr.threshold)]
    if clock_constraint_expr.operator == ">":
        A_row[0] = [x * -1 for x in A_row[0]]
        B_row[0] = -1 * B_row[0]

    if add_epsilon and clock_constraint_expr.equality == False:  # Inequality: Add epsilon.
        B_row[0] -= EPS

    if clock_constraint_expr.operator == "=":
        A_row.append([x * -1 for x in A_row[0]])
        B_row.append(-B_row[0])

    return A_row, B_row


def find_all_semi_realizable_paths(template, max_length):
    """Construct a DP table for all semi-realizable paths in the TA.

    A path is semi-realizable if and only if there exists initial clock
    valuations >= 0 such that that the path is realizable. A DP table is
    returned such that DP[i][j] is a collection (explained below) of all
    semi-realizable paths from the location i to location j.
    We assume there always exists a path from location x to location x of length 0
    (degenerate case).

    Args:
        template: A Template object.
        max_length: Check paths of length <= max_length. Assumed to be >= 1.

    Returns:
        A dict of dict of list of list of lists. DP['i']['j'][k] gives the
        list of semi-realizable paths from location named 'i' to location named
        'j' of length k.
    """
    g = template.graph
    nodes = g.nodes

    DP = {}

    # For debug.
    # c1 = 0
    # c2 = 0
    # c3 = 0

    # Create DP table.
    for i, i_obj in nodes.data("obj"):
        DP[i] = {}
        for j in nodes:
            DP[i][j] = [[] for _ in range(max_length + 1)]
        # Paths of length 0.
        DP[i][i][0].append([i_obj])

    # Add paths of length 1.
    for i, i_obj in nodes.data("obj"):
        for j, edge_dict in g[i].items():
            j_obj = g.nodes.data("obj")[j]
            for e_attr in edge_dict.values():
                e_obj = e_attr["obj"]
                path = [i_obj, e_obj, j_obj]
                if path_realizable_with_initial_valuation(path, icv_constants={}):
                    DP[i][j][1].append(path)

    for l in range(2, max_length + 1):
        # Find paths of length l by examining subpaths of length (p) and (l - p).
        # p1 = i...j, p2 = j...k => p3 = i...j...k
        for p in range(1, l):
            s = l - p
            for i, j, k in product(nodes, repeat=3):
                for p1 in DP[i][j][p]:
                    for p2 in DP[j][k][s]:
                        p3 = p1[:-1] + p2
                        # c1 += l
                        # c2 += 1
                        if p3 in DP[i][k][l]:
                            continue
                        elif path_realizable_with_initial_valuation(
                            p3, icv_constants={}
                        ):
                            DP[i][k][l].append(p3)
                        # c3 += 1
        # print(l, c1, c2, c3)
    return DP


def concatenate_paths(template, p1, p2):
    """Return a list of possible concatenations of given two paths.

    A distinct path for each transition going from the last location of p1 to
    the initial location of p2 is created.

    Args:
        template: A NTA object.
        p1: A list denoting a path. l1-t1-l2-t2..ln
        p2: A list denoting a path. l(n+1)-tn..lm

    Returns:
        A list of paths l1..ln-tx-l(n+1)..lm for each tx.
    """
    res = []
    last = p1[-1].id
    first = p2[0].id
    g = template.graph
    t_name = g.template_name

    # If no transition between the two exists, key error exception is thrown.
    try:
        # Iterate over all transitions from last to first.
        for obj in g[(t_name, last)][(t_name, first)].values():
            t = obj["obj"]
            p = []
            p.extend(p1)
            p.append(t)
            p.extend(p2)
            res.append(p)
    except KeyError:
        pass

    return res


if __name__ == "__main__":
    import uppaalpy as u

    temp = u.NTA.from_xml("examples/generator/test5_6_2.xml").templates[0]
    mypath = convert_to_path(temp, ["l0", 0, "l2", 1, "l3", 2, "l4"])
