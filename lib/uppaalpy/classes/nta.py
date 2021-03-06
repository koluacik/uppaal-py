"""Class definition of UPPAAL NTA."""
import lxml.etree as ET

from .simplethings import Declaration, Query, SystemDeclaration
from .templates import Template


class NTA:
    """Class that holds information about a network of timed automata.

    Attributes:
        declaration: Declaration object..
        templates: List of template objects.
        system: SystemDeclaration object.
        queries: List of Query objects.

    """

    def __init__(self, **kwargs):
        """Initialize NTA from keyword arguments.

        Args:
            **kwargs: Keyword arguments for initializing the NTA. See class docstring.
        """
        self.declaration = kwargs.get("declaration")
        self.templates = kwargs.get("templates") or []
        self.system = kwargs["system"]
        self.queries = kwargs["queries"]

    @classmethod
    def from_xml(cls, path):
        """Given a xml file path, construct an NTA from that xml file."""
        return cls.from_element(ET.parse(path).getroot())

    @classmethod
    def from_element(cls, et):
        """Construct NTA from Element, and return it."""
        kw = {}
        kw["declaration"] = Declaration.from_element(et.find("declaration"))
        kw["templates"] = [
            Template.from_element(template) for template in et.iterchildren("template")
        ]
        kw["system"] = SystemDeclaration.from_element(et.find("system"))
        if et.find("queries") is None:
            kw["queries"] = []
        else:
            kw["queries"] = [
                Query.from_element(query) for query in et.find("queries").iter("query")
            ]
        return cls(**kw)

    def to_element(self):
        """Construct an Element object, and return it."""
        root = ET.Element("nta")

        if self.declaration is not None:
            et_declaration = ET.SubElement(root, "declaration")
            et_declaration.text = self.declaration.text

        for template in self.templates:
            root.append(template.to_element())

        root.append(self.system.to_element())
        queries = ET.SubElement(root, "queries")
        for query in self.queries:
            queries.append(query.to_element())

        return root

    def to_file(self, path, pretty=False):
        """Convert the NTA to an element tree and write it into a file.

        Args:
            path: String denoting the path of the output file.
            pretty: Whether to pretty print.
        """
        (ET.ElementTree(self.to_element())).write(
            path, encoding="utf-8", pretty_print=pretty
        )
