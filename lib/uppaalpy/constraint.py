"""Module for processing constraint strings."""

def string_to_simple(string):
    """Given a constraint string, return a list of simple constraints."""
    return [parse_inequality_simple(s) for s in string.split('&&')]

def parse_inequality_simple(inequality):
    """Given a contraint string, return a simple constraint."""
    # Taken from 
    # https://github.com/jar-ben/tamus/blob/master/uppaalHelpers/\timed_automata.py
    ind = 0
    for i in range(len(inequality)):
        if inequality[i] in ['<', '>', '=']:
            ind = i
            break
    lhs = inequality[0:ind].strip()
    operator = inequality[ind]
    equality = False
    if inequality[ind+1] == '=':
        ind += 1
        equality = True
    rhs = inequality[ind+1:].strip()
    threshold = int(rhs)
    clocks = [c.rstrip().strip() for c in lhs.split('-')]
    return clocks, operator, threshold, equality

def get_invariant_constraints(location):
    if location.invariant is not None:
        return string_to_simple(location.invariant.value)
    return []

def get_guard_constraints(transition):
    if transition.guard is not None:
        return string_to_simple(transition.guard.value)
    return []

def get_constraints(l_or_t):
    try:
        return get_invariant_constraints(l_or_t)
    except:
        return get_guard_constraints(l_or_t)
