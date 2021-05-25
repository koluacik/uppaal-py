from pytest_cases import parametrize

from uppaalpy.classes.class_tests.test_context_cases import DataContext
from uppaalpy.classes.expr import (
    ClockConstraintExpression,
    ClockResetExpression,
    ConstraintExpression,
    UpdateExpression,
)


class DataClockConstraintExpr(DataContext):
    @classmethod
    def exprstr(cls):
        return ["c2 == 3 && 4 < c"] + cls.simple_exprstr()

    @classmethod
    def simple_exprstr(cls):
        return ["c <= 10", "10 >= c", "c1 == 4"]

    @classmethod
    def expr(cls):
        return [ClockConstraintExpression(s, cls.ctx()) for s in cls.exprstr()]


class DataConstraintExpr(DataClockConstraintExpr):
    @classmethod
    def exprstr(cls):
        return cls._simple_exprstr() + super().exprstr()

    @classmethod
    def simple_exprstr(cls):
        return cls._simple_exprstr() + super().simple_exprstr()

    @classmethod
    def _simple_exprstr(cls):
        return ["i >= 15", "15 == j", "j == x"]

    @classmethod
    def expr(cls):
        return [ConstraintExpression(s, cls.ctx()) for s in cls.exprstr()]


class DataClockResetExpr(DataContext):
    @classmethod
    def exprstr(cls):
        return cls.simple_exprstr() + [
            "c = 0, c1 = 0",
        ]

    @classmethod
    def simple_exprstr(cls):
        return [
            "c = 0",
            "c1 = 0",
        ]

    @classmethod
    def expr(cls):
        return [ClockResetExpression(s, cls.ctx()) for s in cls.exprstr()]


class DataUpdateExpr(DataClockResetExpr):
    @classmethod
    def exprstr(cls):
        return (
            [
                "j = i, i = 15",
            ]
            + super().exprstr()
            + cls._simple_exprstr()
        )

    @classmethod
    def _simple_exprstr(cls):
        return [
            "i += 10",
            "i = 10",
            "i -= 10",
            "i = j",
        ]

    @classmethod
    def simple_exprstr(cls):
        return cls._simple_exprstr() + super().simple_exprstr()

    @classmethod
    def expr(cls):
        return [UpdateExpression(s, cls.ctx()) for s in cls.exprstr()]


class DataExpr:
    @classmethod
    def exprstr(cls):
        return DataUpdateExpr.exprstr() + DataConstraintExpr.exprstr()

    @classmethod
    def simple_exprstr(cls):
        return DataUpdateExpr.simple_exprstr() + DataConstraintExpr.exprstr()


class CaseExprStr:
    class C(DataExpr, DataContext):
        pass


class CaseExprTokenize:
    class C(DataExpr):
        pass

    @parametrize("simple_str", C.simple_exprstr())
    def case_no_exception(self, simple_str):
        return simple_str, None

    def case_01(self):
        return "x <= 15", ["x", "<=", "15"]

    def case_02(self):
        return "15 = x", ["15", "=", "x"]

    def case_03(self):
        return "i += 15", ["i", "+=", "15"]

    def case_04(self):
        return "clock > 10", ["clock", ">", "10"]


class CaseUpdateInit:
    class C(DataUpdateExpr, DataContext):
        pass

    @parametrize("string", C.simple_exprstr())
    def case_no_exception(self, string):
        return string, self.C.ctx()


class CaseUpdateExprSplit:
    class C(DataUpdateExpr):
        pass

    @parametrize("complex_str", C.exprstr())
    def case_no_comma(self, complex_str):
        return complex_str, None

    def case_01(self):
        return "x = 10", ["x = 10"]

    def case_02(self):
        return "i += 10, j = 15", ["i += 10", " j = 15"]

    def case_03(self):
        return "i = j,j=i", ["i = j", "j=i"]

    def case_04(self):
        return "i = j ,j=i", ["i = j ", "j=i"]

    def case_05(self):
        return "i = j , j=i, j = 10", ["i = j ", " j=i", " j = 10"]


class CaseUpdateExprJoin:
    class C(DataUpdateExpr):
        pass

    def case_01(self):
        return ["x = 10", "y = 10"], "x = 10, y = 10"

    def case_02(self):
        return ["x = 10"], "x = 10"


class CaseUpdateHandle:
    class C(DataUpdateExpr, DataContext):
        pass

    def case_01(self):
        return (
            UpdateExpression("i += 10", self.C.ctx()),
            self.C.ctx().to_MutableContext(),
            None,
            10,
        )

    def case_02(self):
        return (
            UpdateExpression("i = 10", self.C.ctx()),
            self.C.ctx().to_MutableContext(),
            10,
            None,
        )


class CaseClockResetInit:
    class C(DataClockResetExpr, DataContext):
        pass

    @parametrize("string", C.simple_exprstr())
    def case_all(self, string):
        return string, self.C.ctx()


class CaseConstraintParse:
    class C(DataContext):
        pass

    def case_01(self):
        return "x == 0", self.C.ctx(), False

    def case_02(self):
        return "c >= 15", self.C.ctx(), True


class CaseConstraintHandle:
    class C(DataContext):
        pass

    def case_01(self):
        return "10 >= x", self.C.ctx(), True

    def case_02(self):
        return "x == -10", self.C.ctx(), True

    def case_03(self):
        return "i < j", self.C.ctx(), True

    def case_04(self):
        return "j < i", self.C.ctx(), False


class CaseClockConstraintClock:
    class C(DataContext):
        pass

    def case_01(self):
        return "c1 <= 15", self.C.ctx(), ["c1"], "15"

    def case_02(self):
        return "15 == c2", self.C.ctx(), ["c2"], "15"

    def case_03(self):
        return "x > c", self.C.ctx(), ["c"], "x"

    def case_04(self):
        return "c - c1 < 10", self.C.ctx(), ["c", "c1"], "10"
