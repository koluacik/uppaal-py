"""Unit tests for expressions."""
from pytest_cases.case_parametrizer_new import parametrize_with_cases

from uppaalpy.classes.class_tests.test_expr_cases import (
    CaseClockConstraintClock,
    CaseClockResetInit,
    CaseConstraintHandle,
    CaseConstraintParse,
    CaseExprTokenize,
    CaseUpdateExprJoin,
    CaseUpdateExprSplit,
    CaseUpdateHandle,
    CaseUpdateInit,
)
from uppaalpy.classes.expr import (
    ClockConstraintExpression,
    ClockResetExpression,
    ConstraintExpression,
    Expression,
    UpdateExpression,
)


class TestExpr:
    @parametrize_with_cases("string, res", cases=CaseExprTokenize)
    def test_tokenize(self, string, res):
        r = Expression.tokenize(string)
        assert len(r) == 3
        if res is not None:
            for result, answer in zip(r, res):
                assert result == answer


class TestUpdateExpr:
    @parametrize_with_cases("string, ctx", cases=CaseUpdateInit)
    def test_init(self, string, ctx):
        UpdateExpression(string, ctx)

    @parametrize_with_cases("string, ctx", cases=CaseUpdateInit)
    def test_to_str(self, string, ctx):
        r = UpdateExpression(string, ctx)
        assert string == r.to_string()

    @parametrize_with_cases("string, res", cases=CaseUpdateExprSplit)
    def test_split(self, string, res):
        r = UpdateExpression.split_into_simple(string)
        for i, subexprstr in enumerate(r):
            assert "," not in subexprstr
            if res is not None:
                assert subexprstr == res[i]

    @parametrize_with_cases("strings, res", cases=CaseUpdateExprJoin)
    def test_join_str(self, strings, res):
        r = UpdateExpression.join_strings(strings)
        assert r == res

    @parametrize_with_cases("expr, ctx, res, diff", cases=CaseUpdateHandle)
    def test_handle_update(self, expr, ctx, res, diff):
        old = ctx.get_val(expr.lhs)
        expr.handle_update(ctx)
        new = ctx.get_val(expr.lhs)

        if res is None:
            assert new - old == diff

        else:
            assert new == res


class TestClockReset:
    @parametrize_with_cases("string, ctx", cases=CaseClockResetInit)
    def test_init(self, string, ctx):
        e = ClockResetExpression(string, ctx)
        assert e.clock == e.lhs
        assert ctx.is_clock(e.clock)


class TestConstraintExpr:
    @parametrize_with_cases(
        "string, ctx, is_clock_constraint", cases=CaseConstraintParse
    )
    def test_parse(self, string, ctx, is_clock_constraint):
        expr = ConstraintExpression.parse_expr(string, ctx)
        assert isinstance(expr, ClockConstraintExpression) == is_clock_constraint

    @parametrize_with_cases("string, ctx, res", cases=CaseConstraintHandle)
    def test_handle(self, string, ctx, res):
        expr = ConstraintExpression(string, ctx)
        assert expr.handle_constraint(ctx) == res


class TestClockConstraint:
    @parametrize_with_cases(
        "string, ctx, res_clock, res_thres", cases=CaseClockConstraintClock
    )
    def test_clock_and_thres(self, string, ctx, res_clock, res_thres):
        expr = ClockConstraintExpression(string, ctx)
        assert expr.clocks == res_clock
        assert expr.threshold == res_thres
