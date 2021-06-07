from itertools import product

from lxml import etree as ET
from pytest_cases import parametrize
from uppaalpy.classes.class_tests.test_context_cases import DataContext

from uppaalpy.classes.expr import ClockResetExpression, UpdateExpression
from uppaalpy.classes.simplethings import UpdateLabel

# from uppaalpy.classes.class_tests.test_context_cases import DataContext


class CaseUpdateLabel:
    pass
    label_kinds = ["assignment"]
    # ctx = DataContext.ctx
    label_vals = [
        "c1 = 0",
        "c1 = 0, c2 = 0",
        "i += 1",
        "i = 1",
        "i = k, k = j, j += i",
        "c2 = 0, i = constant3",
        "k -= y",
    ]


class DataLabel:
    label_kinds = [
        "synchronisation",
        "assignment",
        "exponentialrate",
        "testcode",
        "testcodeEnter",
        "testcodeExit",
        "select",
    ]

    label_vals = [
        "foo",
        "bar",
        "x <= 10",
        "x >= 15",
    ]

    label_pos = [(0, 0), (1, 1), (10, 20), (-15, 28)]

    label_element_str = [
        """<label kind="invariant" x="-128" y="64">t&lt;=T[id] &amp;&amp; wcrt'==0</label>""",
        """<label kind="invariant" x="48" y="48">t&lt;=L[id] &amp;&amp; wcrt'==0</label>""",
        """<label kind="invariant" x="-16" y="336">ax&lt;=ci[id][r][0]</label>""",
        """<label kind="invariant" x="8" y="496">ax'==0</label>""",
        """<label kind="guard" x="-24" y="64">t==T[id]</label>""",
        """<label kind="synchronisation" x="-208" y="312">ready!</label>""",
        """<label kind="assignment" x="-208" y="328">updatePriority(ci[id][r][1]), r++</label>""",
        """<label kind="testcodeExit">updatePriority(ci[id][r][1]), r++</label>""",
    ]

    label_kv = product(label_kinds, label_vals)
    label_kvp = product(label_kinds, label_vals, label_pos)
    label_element = [ET.fromstring(s) for s in label_element_str]


class CaseLabelInit:
    class C(DataLabel):
        pass

    @parametrize("kind, val", zip(C.label_kinds, C.label_vals))
    def case_no_position(self, kind, val):
        return (kind, val, None)

    @parametrize("kind, val, pos", zip(C.label_kinds, C.label_vals, C.label_pos))
    def case_with_position(self, kind, val, pos):
        return (kind, val, pos)


class CaseLabelFromElement:
    class C(DataLabel):
        pass

    @parametrize("e", C.label_element)
    def case_1(self, e):
        return e


class CaseLabelToElement:
    class C(DataLabel):
        pass

    @parametrize("e", C.label_element)
    def case_1(self, e):
        return e

class CaseUpdateLabelInit:
    class C(DataLabel, DataContext):
        pass

    def case_updates_none(self):
        ctx = self.C.ctx()
        return "assignment", "i += 15", (0, 1), ctx, None

    def case_updates_not_none(self):
        ctx = self.C.ctx()
        e = UpdateExpression("i += 15", ctx)
        return "assignment", "i += 15", (0, 1), ctx, [e]

    def case_updates_multi(self):
        ctx = self.C.ctx()
        e1 = UpdateExpression("i += 15", ctx)
        e2 = ClockResetExpression("c = 0", ctx)
        return "assignment", "i += 15", (0, 1), ctx, [e1, e2]

class CaseUpdateResets:
    class C(DataLabel, DataContext):
        pass

    def case_01(self):
        return UpdateLabel("assignment", "i += 10", (0, 0), self.C.ctx()), []

    def case_02(self):
        return UpdateLabel("assignment", "c = 0", (0, 0), self.C.ctx()), ["c"]

    def case_03(self):
        return UpdateLabel("assignment", "c = 0, c1 = 0, i += 10", (0, 0), self.C.ctx()), ["c", "c1"]
