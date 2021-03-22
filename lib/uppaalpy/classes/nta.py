"""Class definition of UPPAAL NTA."""
import lxml.etree as ET

from .simplethings import Declaration, Query, SystemDeclaration, Constraint
from .templates import Template
from .constraint_patcher import *


class NTA:
    """Class that holds information about a network of timed automata.

    Attributes:
        declaration: Declaration object..
        templates: List of template objects.
        system: SystemDeclaration object.
        queries: List of Query objects.
        patch_cache: Constraint cache object. Changes on constraints are stored
            here for fast write operations.
        _associated_file: String for denoting the path of the file read. Used
            by constraint patcher. Set by the from_xml method.

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
        self.patch_cache = ConstraintCache(self)
        self._associated_file = ""

    @classmethod
    def from_xml(cls, path):
        """Given a xml file path, construct an NTA from that xml file."""
        obj = cls.from_element(ET.parse(path).getroot())
        obj._associated_file = path
        return obj

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

    def change_transition_constraint(
        self,
        transition,
        *,
        operation=None,
        threshold_delta=None,
        threshold_function=None,
        simple_constraint=None
    ):
        """Insert/remove/update a transition constraint.

        A constraint patch is created to be cached in the patch cache
        for the changed constraint. Operations can be "insert" for insertion,
        "remove" for deletion and "update" for changing the threshold of the
        constraint.

        Args:
            transition: The transition object whose constraints are to
                be changed.
            operation: "insert", "remove", or "update".
            threshold_delta: Integer value used in Update mode. The threshold
                value is set to this value.
            threshold_function: Unary function used in Update mode. The treshold
                x is set to threshold_function(x). Has precedence over
                threshold_delta.
            simple_constraint:
                Insert mode: SimpleConstraint object to be inserted to the
                    guard label (Constraint) of the transition.
                Remove mode: SimpleConstraint object to be removed from the
                    guard label.
                Update mode: SimpleConstraint to be updated with either
                    threshold_delta or threshold_function.


        Insert mode:
        A new SimpleConstraint is inserted to the guard. If no guard exists, one
        at the middlepoint between source and target locations is created. A
        ConstraintInsert is created and cached in the patch cache.

        Remove mode:
        A SimpleConstraint is removed from the guard. If the constraint to be
        removed is the only constraint on the transition, the guard is removed,
        as well. A ConstraintRemove is created and cached in the
        patch cache.

        Update mode:
        The SimpleConstraint object is updated with either threshold_function
        or threshold_delta. A ConstraintUpdate is created and cached in the patch
        cache.
        """
        template = transition.template
        if operation == "insert":
            if transition.guard is None:  # Create guard.
                t_name = template.name.name
                src, dst = (t_name, transition.source), (t_name, transition.target)
                slx, sly = template.graph.nodes[src]["obj"].pos
                dlx, dly = template.graph.nodes[dst]["obj"].pos
                guard_pos = (slx + dlx, sly + dly)

                transition.guard = Constraint(
                    "guard", "", guard_pos, [simple_constraint]
                )
                change = ConstraintInsert(
                    simple_constraint, newly_created=transition.guard
                )

            else:
                transition.guard.constraints.append(simple_constraint)
                change = ConstraintInsert(simple_constraint)

        elif operation == "remove":
            transition.guard.constraints.remove(simple_constraint)
            if transition.guard.constraints == []:
                change = ConstraintRemove(simple_constraint, True)
                transition.guard = None
            else:
                change = ConstraintRemove(simple_constraint)

        else:  # operation == "update"
            old = simple_constraint.threshold
            if threshold_function is not None:
                new = threshold_function(old)
            else:
                new = threshold_delta + old
            change = ConstraintUpdate(simple_constraint, new)
            guard_cs = transition.guard.constraints
            index = guard_cs.index(simple_constraint)
            guard_cs.pop(index)
            guard_cs.insert(index, change.generate_new_constraint())

        patch = ConstraintPatch(template, change, transition_ref=transition)
        self.patch_cache.cache(patch)

    def change_location_constraint(
        self,
        location,
        *,
        operation=None,
        threshold_delta=None,
        threshold_function=None,
        simple_constraint=None
    ):
        """Insert/remove/update a location constraint.

        This method is very similar to change_transition_constraint. The only
        differences are the accessed attributed (guard/invariant) and how
        a possibly new guard/invariant location is determined.
        """
        template = location.template
        if operation == "insert":
            if location.invariant is None:  # Create invariant.
                location.invariant = Constraint(
                    "invariant", "", location.pos, [simple_constraint]
                )
                change = ConstraintInsert(
                    simple_constraint, newly_created=location.invariant
                )
            else:
                location.invariant.constraints.append(simple_constraint)
                change = ConstraintInsert(simple_constraint)

        elif operation == "remove":
            location.invariant.constraints.remove(simple_constraint)
            if location.invariant.constraints == []:
                change = ConstraintRemove(simple_constraint, True)
                location.invariant = None
            else:
                change = ConstraintRemove(simple_constraint)

        else:  # operation == "update"
            old = simple_constraint.threshold
            if threshold_function is not None:
                new = threshold_function(old)
            else:
                new = threshold_delta + old
            change = ConstraintUpdate(simple_constraint, new)
            inv_cs = location.invariant.constraints
            index = inv_cs.index(simple_constraint)
            inv_cs.pop(index)
            inv_cs.insert(index, change.generate_new_constraint())

        patch = ConstraintPatch(template, change, location_ref=location)
        self.patch_cache.cache(patch)

    def flush_constraint_changes(self, out_path):
        """Read the associated_file and write the modified version to new file.

        The xml file the NTA is constructed from is read again and the lines
        are updated according to the patch_cache's update records.
        See: constraint_patcher.py
        """
        with open(self._associated_file) as input_file:
            lines = input_file.readlines()

        self.patch_cache.apply_patches(lines)

        with open(out_path, "w") as output_file:
            output_file.writelines(lines)
