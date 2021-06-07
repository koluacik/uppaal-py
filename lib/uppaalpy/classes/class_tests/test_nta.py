"""Tests for NTA class."""

#TODO: reintroduce random changers

from uppaalpy.classes.context import Context
from uppaalpy.classes.nta import NTA
from uppaalpy.classes.simplethings import Declaration, SystemDeclaration

testcase_dir = "lib/uppaalpy/classes/class_tests/"


def _dec_check(l1, l2):
    def sub(l):
        string = (
            l.replace("UTF-8", "utf-8")
            .replace("'", '"')
            .replace("<formula></formula>", "<formula/>")
            .replace("<comment></comment>", "<comment/>")
            # operators
            .replace(" &lt;", "&lt;")
            .replace(" &gt;", "&gt;")
            .replace(" &amp;", "&amp;")
            .replace("&lt; ", "&lt;")
            .replace("&gt; ", "&gt;")
            .replace("&amp; ", "&amp;")
            .replace("= ", "=")
            .replace(" =", "=")
            .replace(" -", "-")
            .replace("- ", "-")
        )
        return string[:-1] if string[-1] == "\n" else string

    def compare_constraints(l1, l2):
        start1 = l1.index(">") + 1  # '>' in ...y="..">
        end1 = l1.index("<", start1)  # '<' in </label>
        c1 = sorted(l1[start1:end1].split("&amp;&amp;"))

        start2 = l2.index(">") + 1  # '>' in ...y="..">
        end2 = l2.index("<", start2)  # '<' in </label>
        c2 = sorted(l2[start2:end2].split("&amp;&amp;"))

        if len(c1) != len(c2):
            return False

        for i in range(len(c1)):
            if c1[i] != c2[i]:
                print("{} and {} are not equal.".format(c1[i], c2[i]))
                return False
        return True

    str1, str2 = l1.strip(), l2.strip()
    if (
        str1.startswith('<label kind="guard"')
        and str2.startswith('<label kind="guard"')
        or str1.startswith('<label kind="invariant"')
        and str2.startswith('<label kind="invariant"')
    ):
        return compare_constraints(sub(l1), sub(l2))

    return sub(l1) == sub(l2)


class TestNTA:
    """Unit tests for NTA."""

    @staticmethod
    def test_nta_init():
        """Test NTA()."""
        nta = NTA(
            declaration=Declaration("foo"),
            templates=[],
            system=SystemDeclaration("bar"),
            queries=[],
            context=Context.empty()
        )
        assert nta.declaration.text == "foo"
        assert nta.system.text == "bar"
        assert nta.templates == []
        assert nta.queries == []
        assert nta._associated_file == ""
        assert nta._doctype == ""

    @staticmethod
    def test_nta_from_xml():
        """Test NTA.from_xml and NTA.from_element."""
        nta = NTA.from_xml(testcase_dir + "nta_xml_files/small_nta.xml")
        assert len(nta.templates) == 2
        assert nta.declaration.text == "// Place global declarations here."
        assert (
            nta.system.text[:-3]
            == "// Place template instantiations here.\nProcess1 = Test1();\nProcess2 = Test2();\n// List one or more processes to be composed into a system.\nsystem Process1, Process2;"
        )
        assert len(nta.queries) == 1

        nta = NTA.from_xml(testcase_dir + "nta_xml_files/big_nta.xml")
        assert len(nta.templates) == 4
        assert nta.declaration.text == "// Place global declarations here.\nchan c1;"
        assert len(nta.queries) == 1

    @staticmethod
    def test_nta_to_file():
        """Test NTA.to_file."""
        path = testcase_dir + "nta_xml_files/small_nta.xml"
        nta = NTA.from_xml(path)
        nta.to_file("/tmp/out.xml")

        with open(path) as inf, open("/tmp/out.xml") as outf:
            inlines, outlines = inf.readlines(), outf.readlines()

        for i in range(len(inlines)):
            assert _dec_check(inlines[i], outlines[i])

        path = testcase_dir + "nta_xml_files/big_nta.xml"
        nta = NTA.from_xml(path)
        nta.to_file("/tmp/out.xml")

        with open(path) as inf, open("/tmp/out.xml") as outf:
            inlines, outlines = inf.readlines(), outf.readlines()

        for i in range(len(inlines)):
            assert _dec_check(inlines[i], outlines[i])

    @staticmethod
    def test_nta_flush_changes_no_changes():
        """Test NTA.flush_constraint_changes() with no changes."""
        path = testcase_dir + "nta_xml_files/small_nta.xml"
        nta = NTA.from_xml(path)
        nta.flush_constraint_changes("/tmp/out.xml")

        with open(path) as inf, open("/tmp/out.xml") as outf:
            inlines, outlines = inf.readlines(), outf.readlines()

        for i in range(len(inlines)):
            assert _dec_check(inlines[i], outlines[i])

        path = testcase_dir + "nta_xml_files/big_nta.xml"
        nta = NTA.from_xml(path)
        nta.flush_constraint_changes("/tmp/out.xml")

        with open(path) as inf, open("/tmp/out.xml") as outf:
            inlines, outlines = inf.readlines(), outf.readlines()

        for i in range(len(inlines)):
            assert _dec_check(inlines[i], outlines[i])

#     @staticmethod
#     def test_nta_flush_changes1():
#         """Test NTA.flush_constraint_changes() with no changes."""
#         path = testcase_dir + "nta_xml_files/small_nta.xml"
#         out1 = "/tmp/out1.xml"
#         out2 = "/tmp/out2.xml"
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 4, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 4, 0, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 2, 2)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 10, 2, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#     @staticmethod
#     def test_nta_flush_changes2():
#         """Test NTA.flush_constraint_changes() with no changes."""
#         path = testcase_dir + "nta_xml_files/big_nta.xml"
#         out1 = "/tmp/out3.xml"
#         out2 = "/tmp/out4.xml"
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 2, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 0, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 2, 2)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 10, 10, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#     @staticmethod
#     def test_nta_flush_changes3():
#         """Test NTA.flush_constraint_changes() with no changes."""
#         path = testcase_dir + "nta_xml_files/test3.xml"
#         out1 = "/tmp/out5.xml"
#         out2 = "/tmp/out6.xml"
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 1, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 0, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 0, 2)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(3):
#             nta = random_scenario(path, 20, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#     @staticmethod
#     def test_nta_flush_changes4():
#         """Test NTA.flush_constraint_changes() with no changes."""
#         path = testcase_dir + "nta_xml_files/test4.xml"
#         out1 = "/tmp/out7.xml"
#         out2 = "/tmp/out8.xml"
# 
#         for _ in range(10):
#             nta = random_scenario(path, 0, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 3, 1, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 0, 0)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 2, 2, 2)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
# 
#         for _ in range(10):
#             nta = random_scenario(path, 10, 0, 10)
#             nta.flush_constraint_changes(out1)
#             nta.to_file(out2)
# 
#             with open(out1) as flush, open(out2) as write:
#                 inlines, outlines = flush.readlines(), write.readlines()
# 
#             for i in range(len(inlines)):
#                 assert _dec_check(inlines[i], outlines[i])
