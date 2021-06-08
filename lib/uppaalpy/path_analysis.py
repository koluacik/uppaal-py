"""Functions for path analysis."""
from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Union, cast
from ortools.linear_solver import pywraplp
from itertools import product
from uppaalpy.classes.context import Context

from uppaalpy.classes.expr import ClockConstraintExpression
from uppaalpy.classes.nodes import Location
from uppaalpy.classes.templates import Template
from uppaalpy.classes.transitions import Transition


EPS = 2 ** (-10)

# _l : Location | Transition -> Location
# _t : Location | Transition -> Transition
_l = lambda x: cast(Location, x)
_t = lambda x: cast(Transition, x)

Path = List[Union[Location, Transition]]
LI = Tuple[str, str]  # ("id0", "template_name") : location identifier


def path_exists(path: Path) -> bool:
    """Return true if each edge is from previous location to next location."""
    for i in range(1, len(path) - 1, 2):
        if (
            _l(path[i - 1]).id != _t(path[i]).source
            or _l(path[i + 1]).id != _t(path[i]).target
        ):
            return False
    return True


def find_used_clocks(path: Path) -> List[str]:
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


def convert_to_path(
    template: Template, lst: List[Union[int, str]]
) -> List[Union[Location, Transition]]:
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
            path.append(template.graph._transitions[cast(int, rep)])
        else:
            path.append(template.graph._named_locations[cast(str, rep)])
    return path


def path_realizable(
    path: Path,
    validate_path: bool = False,
    validate_state: bool = False,
    add_epsilon: bool = False,
) -> Tuple[bool, List[float]]:
    """Given a path, construct an LP and return results.

    See: path_realizable_with_initial_valuation from this module.
    """
    return path_realizable_with_initial_valuation(
        path, validate_path, validate_state, add_epsilon
    )


def path_realizable_with_initial_valuation(
    path: Path,
    validate_path: bool = False,
    validate_state: bool = False,
    add_epsilon: bool = False,
    icv_constants: Optional[Dict[str, int]] = None,
    clocks: List[str] = None,
) -> Tuple[bool, List[float]]:
    """Given a path, construct an LP and return results.

    Args:
        path: List of alternating location and transitions.
        validate_path: Check whether each transition is actually between
            the previous location and the next location.
        validate_state: Whether to check non-clock constraints for path
            realizability.
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

    ctx = path[0].template.context.to_MutableContext()

    # Find clock names.
    if clocks == None:
        clocks = find_used_clocks(path)

    clock_to_delay: Dict[str, List[int]] = dict()

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
        l = _l(path[i])
        if l.invariant is not None:
            for c in l.invariant.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(
                    clock_to_delay, c, var_count, ctx, add_epsilon, validate_state
                )
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Transition
        t = _t(path[i + 1])
        if t.guard is not None:
            for c in t.guard.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(
                    clock_to_delay, c, var_count, ctx, add_epsilon, validate_state
                )
                for k in range(len(a)):
                    A.append(a[k])
                    B.append(b[k])

        # Resets and updates
        resets_in_transition, updates_in_transition = [], []
        if t.assignment is not None:
            resets_in_transition = t.assignment.get_resets()
            updates_in_transition = t.assignment.get_other_updates()
        for c in resets_in_transition:
            clock_to_delay[c] = []
        for u in updates_in_transition:
            u.handle_update(ctx)

        # Target location
        l = _l(path[i + 2])
        if l.invariant is not None:
            for c in l.invariant.constraints:
                if not isinstance(c, ClockConstraintExpression):
                    continue
                a, b = compute_constraint(
                    clock_to_delay, c, var_count, ctx, add_epsilon, validate_state
                )
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

    return False, []


def get_resets(transition, clocks):
    """Find clocks to be reset upon taking the transition.

    Args:
        transition: A transition object.
        clocks: List of used clocks in the analysis.

    Returns:
        list of clocks to be reset.
    """
    # TODO: delete me
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
    clock_to_delay: Dict[str, List[int]],
    exp: ClockConstraintExpression,
    variable_count: int,
    ctx: Context,
    add_epsilon: bool = False,
    skip_var_threshold: bool = False,
) -> Tuple[List[List[int]], List[int]]:
    """Construct a row of the Linear Program.

    The satisfiability of the constraints with variable thresholds depends on
    the current state. For this reason they should be omitted in
    semi-realizability checking for path segments considered while populating
    the DP table.

    Args:
        clock_to_delay: Dictionary of list of ints. clock_to_delay['x'] gives
            a list of delay variables for the locations visited since the last
            reset of clock 'x'.
        exp: ClockConstraintExpression
        variable_count: Int for determining the row size.
        ctx: Context used to determine the valuations of variables.
        add_epsilon: Whether to treat '<=' as '<' by adding an epsilon value to
            the threshold.
        skip_var_threshold: Whether to skip constraints of form clock < variable
    """

    if ctx.is_variable(exp.threshold) and skip_var_threshold:
        return [], []

    A_row = [[0 for _ in range(variable_count)]]
    for delay_var in clock_to_delay[exp.clocks[0]]:
        A_row[0][delay_var] = 1

    if len(exp.clocks) == 2:  # clock difference
        for delay_var in clock_to_delay[exp.clocks[1]]:
            A_row[0][delay_var] -= 1

    # TODO: get value from context
    B_row = [ctx.get_val(exp.threshold)]
    if exp.operator == ">":
        A_row[0] = [x * -1 for x in A_row[0]]
        B_row[0] = -1 * B_row[0]

    if add_epsilon and exp.equality == False:  # Inequality: Add epsilon.
        B_row[0] -= EPS

    if exp.operator == "=":
        A_row.append([x * -1 for x in A_row[0]])
        B_row.append(-B_row[0])

    return A_row, B_row


def find_all_semi_realizable_paths(
    template: Template, max_length: int
) -> Dict[LI, Dict[LI, List[List[Path]]]]:
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

    DP: Dict[LI, Dict[LI, List[List[Path]]]] = {}

    # Create DP table.
    for i, i_obj in nodes.data("obj"):  # type: ignore
        DP[i] = {}
        for j in nodes:
            DP[i][j] = [[] for _ in range(max_length + 1)]
        # Paths of length 0.
        DP[i][i][0].append([i_obj])

    # Add paths of length 1.
    for i, i_obj in nodes.data("obj"):  # type: ignore
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
    return DP


def check_dp(init: LI, target: LI, table: Dict[LI, Dict[LI, List[List[Path]]]]) -> bool:
    pps = table[init][target]
    for ps in pps:
        for p in ps:
            if path_realizable(p, True, True):
                return True
    return False


def find_reachable_locations(
    template: Template, table: Dict[LI, Dict[LI, List[List[Path]]]]
) -> None:
    """Mark the TAGraph of the given template for reachability.

    Reachability of a location can be checked with
    template.graph.nodes[("template_name", "location_id")]["tag"]
    """
    g = template.graph
    tn = g.template_name

    def f(x: str):
        return (tn, x)

    init = f(g.initial_location)

    for node in g:
        g.nodes[node]["tag"] = False
    q = deque()  # type: deque[LI]
    q.append(init)

    while q:
        n = q.popleft()
        if check_dp(init, n, table):
            g.nodes[n]["tag"] = True
            for succ in g.nodes[n]:
                q.append(succ)


def reachability_analysis(
    template: Template, table: Dict[LI, Dict[LI, List[List[Path]]]]
) -> Set[LI]:
    """Given a TA template and a path length limit, return reachable locations."""

    res = set()

    find_reachable_locations(template, table)

    for node, is_tagged in template.graph.nodes.data("tagged"):  # type: ignore
        if is_tagged:
            res.add(node)

    return res


def furthest_reachable(
    template: Template, target_set: Set[LI], table: Dict[LI, Dict[LI, List[List[Path]]]]
) -> Set[LI]:

    find_reachable_locations(template, table)
    gp = template.graph.reverse()
    q_act, q_alt = deque(target_set), deque()
    flag = False
    res: Set[LI] = set()

    while q_act:
        while q_act:
            n = q_act.popleft()
            if gp.nodes[n]["tag"]:
                flag = True
                res.add(n)
            if not flag:
                for succ in gp[n]:
                    q_alt.append(succ)
        if not flag:
            # breaks from the outer loop if q_alt is empty or flag is True
            q_act = q_alt
            q_alt = deque()

    return res



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
    # TODO: delete me
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
