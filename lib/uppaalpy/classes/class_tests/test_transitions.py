"""Unit tests for Locations and BranchPoints."""
import lxml.etree as ET
import pytest
from uppaalpy.classes.class_tests.test_context_cases import DataContext

from uppaalpy.classes.simplethings import ConstraintLabel
from uppaalpy.classes.transitions import Nail, Transition


class TestTransition:
    """Transition tests."""

    class C(DataContext):
        pass

    def test_transition_init(self):
        """Test Tranisiton()."""
        t1 = Transition(source="id1", target="id1")
        assert t1.source == "id1"
        assert t1.target == "id1"
        assert t1.nails == []

        t2 = Transition(source="id1", target="id2", nails=[Nail(1, 3), Nail(2, 2)])
        assert t2.nails[0].pos == (1, 3)
        assert t2.nails[1].pos == (2, 2)

        t3 = Transition(
            source="id1", target="id2", guard=ConstraintLabel("guard", "x == 0", (1, 3), self.C.ctx())
        )
        assert t3.guard is not None

        with pytest.raises(KeyError):
            assert Transition()

        with pytest.raises(KeyError):
            assert Transition(source="id1")

        with pytest.raises(KeyError):
            assert Transition(source="id2")

    def test_transition_from_element(self):
        """Test Transition.from_element()."""
        t1 = Transition.from_element(
            ET.fromstring(
                """
            <transition>
                    <source ref="id5"/>
                    <target ref="id17"/>
            </transition>
            """
            ), self.C.ctx()
        )

        assert t1.source == "id5"
        assert t1.target == "id17"
        assert t1.guard is None
        assert t1.assignment is None

        t2 = Transition.from_element(
            ET.fromstring(
                """
		<transition>
			<source ref="id5"/>
			<target ref="id17"/>
			<label kind="guard" x="-416" y="512">x == 10</label>
			<label kind="assignment" x="-416" y="528">counter=-1, detected=-1, slot_no[id]=-1,
aux_vec=zero_vec, first[id]=zero_vec, 
sent_info=0</label>
			<label kind="comments" x="-236" y="838">Broadcast information about collisions if any</label>
			<nail x="-72" y="544"/>
			<nail x="-464" y="544"/>
			<nail x="-464" y="40"/>
		</transition>
                """
            ), self.C.ctx()
        )

        assert t2.nails[2].pos == (-464, 40)
        assert t2.guard is not None
        assert t2.assignment is not None
        assert t2.comments is not None
        assert t2.synchronisation is None

    def test_transition_to_element(self):
        """Test Transition.to_element()."""
        e1 = Transition.from_element(
            ET.fromstring(
                """
            <transition>
                    <source ref="id5"/>
                    <target ref="id17"/>
            </transition>
            """
            ), self.C.ctx()
        ).to_element()

        assert e1.find("source").get("ref") == "id5"
        assert e1.find("target").get("ref") == "id17"

        e2 = Transition.from_element(
            ET.fromstring(
                """
		<transition>
			<source ref="id5"/>
			<target ref="id17"/>
			<label kind="guard" x="-416" y="512">x == 10</label>
			<label kind="assignment" x="-416" y="528">counter=-1, detected=-1, slot_no[id]=-1,
aux_vec=zero_vec, first[id]=zero_vec, 
sent_info=0</label>
			<label kind="comments" x="-236" y="838">Broadcast information about collisions if any</label>
			<nail x="-72" y="544"/>
			<nail x="-464" y="544"/>
			<nail x="-464" y="40"/>
		</transition>
                """
            ), self.C.ctx()
        ).to_element()

        labels = e2.findall("label")
        assert labels[0].get("kind") == "guard"
        assert labels[1].get("kind") == "assignment"
        assert labels[2].get("kind") == "comments"


class TestNail:
    """Nail tests."""

    @staticmethod
    def test_nail_init():
        """Test Nail()."""
        n = Nail(13, 26)
        assert n.pos == (13, 26)

        with pytest.raises(TypeError):
            assert Nail()  # Ignore the type error here by pylint/pyright.

    @staticmethod
    def test_nail_from_element():
        """Test Nail.from_element()."""
        n = Nail.from_element(ET.fromstring('<nail x="-72" y="544"/>'))
        assert n.pos == (-72, 544)

    @staticmethod
    def test_nail_to_element():
        """Test Nail.to_element()."""
        n = Nail(-72, 44)
        assert n.pos == (-72, 44)
