from uppaalpy.classes.class_tests.test_context_cases import DataContext
from uppaalpy.classes.constraint_patcher import ConstraintRemove
from uppaalpy.classes.expr import ClockConstraintExpression


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
