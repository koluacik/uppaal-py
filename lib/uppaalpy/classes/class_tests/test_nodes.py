"""Unit tests for Locations and BranchPoints."""
from typing import cast
import lxml.etree as ET
import pytest
from uppaalpy.classes.class_tests.test_context_cases import DataContext
from uppaalpy.classes.expr import ClockConstraintExpression

from uppaalpy.classes.nodes import BranchPoint, Location, Node
from uppaalpy.classes.simplethings import ConstraintLabel, Name


class TestNode:
    """Node tests."""
    class C(DataContext):
        pass

    def test_generate_dict(self):
        """Test initialization data generated from an Element."""
        n1 = Node.generate_dict(
            ET.fromstring(
                """
        <location id="id1" x="192" y="384">
            <name x="208" y="392">Stop</name>
        </location>
            """
            ), self.C.ctx()
        )
        assert n1["id"] == "id1"
        assert n1["pos"] == (192, 384)
        assert n1["name"].name == "Stop"
        assert n1["name"].pos == (208, 392)

        n2 = Node.generate_dict(
            ET.fromstring(
                """
        <location id="id3" x="96" y="256">
            <name x="40" y="240">Appr</name>
            <label kind="invariant" x="32" y="264">x&lt;=20</label>
        </location>
            """
            ), self.C.ctx()
        )
        assert n2["id"] == "id3"
        assert n2["pos"] == (96, 256)
        assert n2["name"].name == "Appr"
        assert n2["name"].pos == (40, 240)
        assert n2["invariant"].kind == "invariant"
        assert n2["invariant"].value == "x<=20"
        assert n2["invariant"].pos == (32, 264)

        n3 = Node.generate_dict(
            ET.fromstring(
                """
                <location id="id5" x="144" y="-88">
                        <name x="134" y="-118">C1</name>
                        <label kind="invariant" x="152" y="-72">x'==2</label>
                        <label kind="exponentialrate" x="134" y="-73">3</label>
                </location>
            """
            ), self.C.ctx()
        )
        assert n3["id"] == "id5"
        assert n3["pos"] == (144, -88)
        assert n3["name"].name == "C1"
        assert n3["name"].pos == (134, -118)
        assert n3["invariant"].kind == "invariant"
        assert n3["invariant"].value == "x'==2"
        assert n3["invariant"].pos == (152, -72)
        assert n3["exponentialrate"].kind == "exponentialrate"
        assert n3["exponentialrate"].value == "3"
        assert n3["exponentialrate"].pos == (134, -73)

        n4 = Node.generate_dict(
            ET.fromstring(
                """
                <location id="id2" x="8" y="-17">
                        <name x="-26" y="-17">Off</name>
                        <label kind="testcodeEnter">expect_off();</label>
                </location>
            """
            ), self.C.ctx()
        )
        assert n4["id"] == "id2"
        assert n4["pos"] == (8, -17)
        assert n4["name"].name == "Off"
        assert n4["name"].pos == (-26, -17)
        assert n4["testcodeEnter"].kind == "testcodeEnter"
        assert n4["testcodeEnter"].value == "expect_off();"
        assert n4["testcodeEnter"].pos == None
        assert n4["committed"] == False

        n5 = Node.generate_dict(
            ET.fromstring(
                """
                <location id="id9" x="88" y="336">
                        <committed/>
                </location>
            """
            ), self.C.ctx()
        )
        assert n5["id"] == "id9"
        assert n5["pos"] == (88, 336)
        assert n5["committed"] == True


class TestBranchPoint:
    """Unit tests for branchpoints."""
    class C(DataContext):
        pass

    @staticmethod
    def test_branchpoint_init():
        """Test the init method."""
        bp = BranchPoint(id="id3", pos=(3, 4))
        assert bp.id == "id3"
        assert bp.pos == (3, 4)
        assert bp.tag == "branchpoint"

        bp = BranchPoint(id="id15", pos=(-13, 7))
        assert bp.id == "id15"
        assert bp.pos == (-13, 7)
        assert bp.tag == "branchpoint"

        with pytest.raises(KeyError):
            assert BranchPoint(id=13)

    def test_branchpoint_from_element(self):
        """Test the from_element method."""
        xml1 = ET.fromstring('<branchpoint id="id4" x="-25" y="-25"></branchpoint>')
        bp1 = BranchPoint.from_element(xml1, self.C.ctx())

        assert bp1.id == "id4"
        assert bp1.pos == (-25, -25)

        xml2 = ET.fromstring('<branchpoint id="id7" x="48" y="-48"></branchpoint>')
        bp2 = BranchPoint.from_element(xml2, self.C.ctx())

        assert bp2.id == "id7"
        assert bp2.pos == (48, -48)

    def test_branchpoint_to_element(self):
        """Test the to_element method."""
        xml1 = ET.fromstring('<branchpoint id="id4" x="-25" y="-25"></branchpoint>')
        e1 = BranchPoint.from_element(xml1, self.C.ctx()).to_element()

        assert e1.get("id") == "id4"
        assert e1.get("x") == "-25"
        assert e1.get("y") == "-25"

        xml2 = ET.fromstring('<branchpoint id="id7" x="48" y="-48"></branchpoint>')
        e2 = BranchPoint.from_element(xml2, self.C.ctx()).to_element()

        assert e2.get("id") == "id7"
        assert e2.get("x") == "48"
        assert e2.get("y") == "-48"


class TestLocation:
    """Tests for Location class."""

    class C(DataContext):
        pass

    def test_location_init(self):
        """Test the init method."""
        l1 = Location(id="id1", pos=(1, 3))
        assert l1.id == "id1"
        assert l1.pos == (1, 3)

        l2 = Location(id="id1", pos=(1, 3), name=Name("loc1", (4, 8)))
        assert l2.id == "id1"
        assert l2.pos == (1, 3)
        assert l2.pos == (1, 3)
        assert l2.name.name == "loc1"
        assert l2.name.pos == (4, 8)

        l3 = Location(
            id="id1",
            pos=(1, 3),
            name=Name("loc1", (4, 8)),
            invariant=ConstraintLabel("invariant", "x <= 13", (14, 28), self.C.ctx()),
        )
        assert l3.id == "id1"
        assert l3.pos == (1, 3)
        assert l3.pos == (1, 3)
        assert l3.name.name == "loc1"
        assert l3.name.pos == (4, 8)
        assert l3.invariant.kind == "invariant"

        with pytest.raises(KeyError):
            assert Location(id="id1")

        with pytest.raises(KeyError):
            assert Location(pos=(1, 3))

    def test_location_from_element(self):
        """Test the from_element method."""
        l1 = Location.from_element(
            ET.fromstring(
                """
        <location id="id1" x="192" y="384">
            <name x="208" y="392">Stop</name>
        </location>
            """
            ), self.C.ctx()
        )

        assert l1.id == "id1"
        assert l1.pos == (192, 384)
        assert l1.committed == False
        assert l1.urgent == False

        l2 = Location.from_element(
            ET.fromstring(
                """
        <location id="id3" x="96" y="256">
            <name x="40" y="240">Appr</name>
            <label kind="invariant" x="32" y="264">x&lt;=20</label>
            <label kind="exponentialrate" x="134" y="-73">3</label>
            <label kind="testcodeEnter">expect_off();</label>
            <committed/>
        </location>
            """
            ), self.C.ctx()
        )

        assert l2.id == "id3"
        assert l2.pos == (96, 256)
        assert l2.committed == True
        assert l2.urgent == False
        assert l2.invariant is not None
        assert l2.testcodeEnter is not None

    def test_location_to_element(self):
        """Test the to_element method."""
        e1 = Location.from_element(
            ET.fromstring(
                """
        <location id="id1" x="192" y="384">
            <name x="208" y="392">Stop</name>
        </location>
            """
            ), self.C.ctx()
        ).to_element()

        assert e1.get("id") == "id1"
        assert e1.get("x") == "192"
        assert e1.get("y") == "384"

        e2 = Location.from_element(
            ET.fromstring(
                """
        <location id="id3" x="96" y="256">
            <name x="40" y="240">Appr</name>
            <label kind="invariant" x="32" y="264">x&lt;=20</label>
            <label kind="exponentialrate" x="134" y="-73">3</label>
            <label kind="testcodeEnter">expect_off();</label>
            <committed/>
        </location>
            """
            ), self.C.ctx()
        ).to_element()

        assert e2.get("id") == "id3"
        assert e2.get("x") == "96"
        assert e2.get("y") == "256"
        labels = e2.findall("label")
        assert labels[0].get("kind") == "invariant"
        assert labels[1].get("kind") == "exponentialrate"
        assert labels[2].get("kind") == "testcodeEnter"
        assert e2.find("committed") in e2
        assert e2.find("urgent") not in e2

    def test_location_get_constrasints(self):
        """Test Location.get_constraints()."""
        l1 = Location.from_element(
            ET.fromstring(
                """
        <location id="id1" x="192" y="384">
            <name x="208" y="392">Stop</name>
        </location>
            """
            ), self.C.ctx()
        )

        assert l1.get_constraints() == []

        l2 = Location.from_element(
            ET.fromstring(
                """
        <location id="id3" x="96" y="256">
            <name x="40" y="240">Appr</name>
            <label kind="invariant" x="32" y="264">c&lt;=20</label>
            <label kind="exponentialrate" x="134" y="-73">3</label>
            <label kind="testcodeEnter">expect_off();</label>
            <committed/>
        </location>
            """
            ), self.C.ctx()
        )

        cs = l2.get_constraints()
        assert len(cs) == 1
        c = cast(ClockConstraintExpression, cs[0])
        assert c.clocks == ["c"]
        assert c.operator == "<"
        assert c.threshold == "20"
        assert c.equality == True
