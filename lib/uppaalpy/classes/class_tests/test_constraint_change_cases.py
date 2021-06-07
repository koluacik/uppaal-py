from uppaalpy.classes.class_tests.test_context_cases import DataContext
from uppaalpy.classes.constraint_patcher import ConstraintInsert, ConstraintRemove, ConstraintUpdate
from uppaalpy.classes.expr import ClockConstraintExpression
from uppaalpy.classes.simplethings import ConstraintLabel


class CaseCRInit:
    class C(DataContext):
        pass

    def case_01(self):
        return ClockConstraintExpression("c > 15", self.C.ctx()), False

    def case_02(self):
        return ClockConstraintExpression("c > 15", self.C.ctx()), True

    def case_03(self):
        return ClockConstraintExpression("c > 15", self.C.ctx()), None


class CaseRFind:
    class C(DataContext):
        pass

    def case_01(self):
        return ClockConstraintExpression("c == 15", self.C.ctx()), ["c == 15"], 0

    def case_02(self):
        return (
            ClockConstraintExpression("c == 15", self.C.ctx()),
            ["c == 15", "c1 > 13"],
            0,
        )

    def case_03(self):
        return (
            ClockConstraintExpression("c == 15", self.C.ctx()),
            ["c1 > 13", "c == 15"],
            1,
        )

    def case_04(self):
        return (
            ClockConstraintExpression("c == 15", self.C.ctx()),
            ["c1 > 13", "c2 == 15"],
            -1,
        )

    def case_05(self):
        return ClockConstraintExpression("c == 15", self.C.ctx()), [], -1


class CaseRPatch:
    class C(DataContext):
        pass

    def case_01(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 5 &amp;&amp; i &lt; 5</label>\n',
            "		</location>\n",
        ]
        res = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">i &lt; 5</label>\n',
            "		</location>\n",
        ]
        expr = ClockConstraintExpression("c < 5", self.C.ctx())
        cr = ConstraintRemove(expr, False)

        return cr, lines, 1, res

    def case_02(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 5</label>\n',
            "		</location>\n",
        ]
        res = [
            '		<location id="id0" x="0" y="0">\n',
            "		</location>\n",
        ]
        expr = ClockConstraintExpression("c < 5", self.C.ctx())
        cr = ConstraintRemove(expr, True)

        return cr, lines, 1, res

    def case_03(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 5</label>\n',
            "		</location>\n",
        ]

        res = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            "		</location>\n",
        ]

        expr = ClockConstraintExpression("c < 5", self.C.ctx())
        cr = ConstraintRemove(expr, True)

        return cr, lines, 2, res

    def case_04(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 5</label>\n',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>\n',
            "		</location>\n",
        ]
        res = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="name" x="18" y="-34">location0</label>\n',
            '			<label kind="exponentialrate" x="18" y="-34">foo</label>\n',
            "		</location>\n",
        ]

        expr = ClockConstraintExpression("c < 5", self.C.ctx())
        cr = ConstraintRemove(expr, True)

        return cr, lines, 2, res

    def case_05(self):
        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">5 == c</label>\n',
            "		</transition>\n",
        ]
        res = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            "		</transition>\n",
        ]
        expr = ClockConstraintExpression("5 == c", self.C.ctx())
        cr = ConstraintRemove(expr, True)

        return cr, lines, 3, res


class CaseIinit:
    class C(DataContext):
        pass

    def case_01(self):
        return ClockConstraintExpression("c > 15", self.C.ctx()), None


class CaseIPatch:
    class C(DataContext):
        pass

    def case_01(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">c1 - c &lt;= 5</label>\n',
            "		</location>\n",
        ]

        expr = ClockConstraintExpression("c1 - c <= 5", self.C.ctx())
        invariant = ConstraintLabel("invariant", "", (18, -34), self.C.ctx(), [expr])
        ci = ConstraintInsert(expr, invariant)

        return ci, lines, lines_expected, 0, 0


    def case_02(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">x - y &lt;= 5 &amp;&amp; c == 3</label>\n',
            "		</location>\n",
        ]

        expr = ClockConstraintExpression("c == 3", self.C.ctx())
        ci = ConstraintInsert(expr)

        return ci, lines, lines_expected, 1, 0

    def case_03(self):
        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">c == 5</label>\n',
            "		</transition>\n",
        ]

        expr = ClockConstraintExpression("c == 5", self.C.ctx())
        guard = ConstraintLabel("guard", "", (18, -34), self.C.ctx(), [expr])
        ci = ConstraintInsert(expr, guard)

        return ci, lines, lines_expected, 2, 0

    def case_04(self):
        lines = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        lines_expected = [
            "		<transition>\n",
            '			<source ref="id0"/>\n',
            '			<source ref="id1"/>\n',
            '			<label kind="guard" x="18" y="-34">clock2 == 5 &amp;&amp; c == 5</label>\n',
            '			<label kind="synchronisation" x="18" y="-34">foo</label>\n',
            "		</transition>\n",
        ]

        expr = ClockConstraintExpression("c == 5", self.C.ctx())
        ci = ConstraintInsert(expr)

        return ci, lines, lines_expected, 3, 0

class CaseUInit:
    class C(DataContext):
        pass

    def case_01(self):
        c = ClockConstraintExpression("c == 3", self.C.ctx())
        cu = ConstraintUpdate(c, "11")

        return c, cu, "3", "11"

class CaseUFind:
    class C(DataContext):
        pass
    c = ClockConstraintExpression("c > 10", C.ctx())
    cu = ConstraintUpdate(c, "13")

    def case_01(self):
        return self.cu, ["c &gt; 10"], 0

    def case_02(self):
        return self.cu, ["c1 == 10", "c &gt; 10"], 1

    def case_03(self):
        return self.cu, ["c1 &gt; 13"], None

class CaseUPatch:
    class C(DataContext):
        pass

    def case_01(self):
        lines = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 5 &amp;&amp; y &lt; 5</label>\n',
            "		</location>\n",
        ]

        lines_expected = [
            '		<location id="id0" x="0" y="0">\n',
            '			<label kind="invariant" x="18" y="-34">c &lt; 10 &amp;&amp; y &lt; 5</label>\n',
            "		</location>\n",
        ]

        c = ClockConstraintExpression("c < 5", self.C.ctx())
        cu = ConstraintUpdate(c, "10")

        return cu, lines, 1, lines_expected

