from uppaalpy.classes.context import Context


class DataContext:
    @classmethod
    def ctx(cls):
        return Context(
            {"c1", "c2", "c"},
            {"x": -10, "y": 0, "constant3": 3},
            {"i": -1, "j": 4, "k": 10},
        )
