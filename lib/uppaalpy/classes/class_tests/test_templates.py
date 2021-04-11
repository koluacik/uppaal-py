"""Unit tests for Templates and TAGraphs."""
import lxml.etree as ET
from uppaalpy.classes.nodes import Location
from uppaalpy.classes.simplethings import Constraint, Name
from uppaalpy.classes.tagraph import TAGraph
from uppaalpy.classes.templates import Template
from uppaalpy.classes.transitions import Transition

from .helpers import testcase_dir


class TestTemplate:
    """Template tests."""

    @staticmethod
    def test_template_init():
        """Test default values set by Template()."""
        template = Template()
        assert template.name.name == ""
        assert template.name.pos == (0, 0)
        assert template.parameter.tag == "parameter"
        assert template.parameter.text == ""
        assert template.declaration.tag == "declaration"
        assert template.declaration.text == ""

    @staticmethod
    def test_template_from_element():
        """Test Template.from_element()."""
        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test1.xml").getroot()
        )
        assert t.name.name == "Test1"
        assert t.parameter == None
        assert t.declaration is not None

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test2.xml").getroot()
        )
        assert t.name.name == "Test2"
        assert t.parameter == None
        assert t.declaration is not None

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test3.xml").getroot()
        )
        assert t.name.name == "P"
        assert t.parameter.text == "const id_t pid"
        assert t.declaration.text == "clock x;\nconst int k = 2;"

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test4.xml").getroot()
        )
        assert t.name.name == "Train"
        assert t.parameter.text == "const id_t id"
        assert t.declaration.text == "clock x;"

    @staticmethod
    def test_template_to_element():
        """Test Template.to_element()."""
        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test1.xml").getroot()
        ).to_element()
        assert t.find("name").text == "Test1"
        assert t.find("parameter") == None

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test2.xml").getroot()
        ).to_element()
        assert t.find("name").text == "Test2"
        assert t.find("parameter") == None

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test3.xml").getroot()
        ).to_element()
        assert t.find("name").text == "P"
        assert t.find("parameter").text == "const id_t pid"
        assert t.find("declaration").text == "clock x;\nconst int k = 2;"

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test4.xml").getroot()
        ).to_element()
        assert t.find("name").text == "Train"
        assert t.find("parameter").text == "const id_t id"
        assert t.find("declaration").text == "clock x;"

    @staticmethod
    def test_template_parse_clocks():
        """Test initializing clock list from the declaration field."""
        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test1.xml").getroot()
        )
        assert t.clocks == ["x", "y"]

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test2.xml").getroot()
        )
        assert t.clocks == ["x"]

        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test6.xml").getroot()
        )
        assert t.clocks == ["x", "y", "c3", "clock4", "clock5"]


class TestTAGraph:
    """Unit tests for TAGraphs."""

    @staticmethod
    def test_tagraph_init():
        """Test initial values set by TAGraph()."""
        graph = TAGraph(None)
        assert graph.initial_location == ""
        assert graph.template == None
        assert graph.template_name == ""
        assert graph._named_locations == {}
        assert graph._transitions == []

    @staticmethod
    def test_tagraph_add_location():
        """Test adding a location to the graph."""
        graph = TAGraph(None)
        loc = Location(
            id="id0",
            pos=(0, 0),
            name=Name("loc0", (0, 0)),
            invariant=Constraint("invariant", "x <= 3", (0, 0)),
        )
        graph.add_location(loc)
        assert graph._named_locations["loc0"] is not None
        assert graph.nodes(data="obj")[("", "id0")] == loc

        loc2 = Location(
            id="id1",
            pos=(1, 1),
            invariant=Constraint("invariant", "x <= 4", (1, 1)),
        )
        graph.add_location(loc2)
        assert len(graph._named_locations.keys()) == 1
        assert graph.nodes(data="obj")[("", "id1")] == loc2

    @staticmethod
    def test_tagraph_add_transition():
        """Test adding a transition to the graph."""
        graph = TAGraph(None)
        loc = Location(
            id="id0",
            pos=(0, 0),
            name=Name("loc0", (0, 0)),
            invariant=Constraint("invariant", "x <= 3", (0, 0)),
        )
        graph.add_location(loc)

        loc2 = Location(
            id="id1",
            pos=(1, 1),
            invariant=Constraint("invariant", "x <= 4", (1, 1)),
        )
        graph.add_location(loc2)

        trans = Transition(source="id0", target="id1")
        graph.add_transition(trans)

        assert graph._transitions[0] == trans
        assert graph[("", "id0")][("", "id1")][0]["obj"] == trans

    @staticmethod
    def test_tagraph_init_with_template():
        """Test TAGraph initialization."""
        t = Template.from_element(
            ET.parse(testcase_dir + "template_xml_files/test1.xml").getroot()
        )
        g = t.graph
        assert g.template == t
        assert g.template_name == t.name.name
        assert list(g._named_locations.keys()) == ["l2", "l1", "l0"]
        assert g._named_locations["l2"].id == "id0"
        assert g._named_locations["l1"].id == "id1"
        assert g._named_locations["l0"].id == "id2"
        assert g.initial_location == "id2"

        assert g._transitions[0].source == "id2"
        assert g._transitions[1].source == "id1"
        assert g._transitions[2].source == "id1"
        assert g._transitions[3].source == "id2"

        assert g._transitions[0].target == "id0"
        assert g._transitions[1].target == "id0"
        assert g._transitions[2].target == "id0"
        assert g._transitions[3].target == "id1"

    @staticmethod
    def test_tagraph_get_nodes():
        """Test TAGraph.get_nodes()."""
        graph = TAGraph(None)
        loc = Location(
            id="id0",
            pos=(0, 0),
            name=Name("loc0", (0, 0)),
            invariant=Constraint("invariant", "x <= 3", (0, 0)),
        )
        graph.add_location(loc)

        loc2 = Location(
            id="id1",
            pos=(1, 1),
            invariant=Constraint("invariant", "x <= 4", (1, 1)),
        )
        graph.add_location(loc2)

        nlist = graph.get_nodes()
        assert nlist[0] == loc
        assert nlist[1] == loc2
