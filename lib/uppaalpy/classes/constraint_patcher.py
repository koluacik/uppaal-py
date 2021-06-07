"""Class definitions for fast constraint changes."""

from abc import ABCMeta, abstractmethod
from copy import copy
from typing import List, Optional, Union, cast

from uppaalpy.classes import nodes as n
from uppaalpy.classes import nta
from uppaalpy.classes import templates as te
from uppaalpy.classes import transitions as tr
from uppaalpy.classes.expr import ClockConstraintExpression
from uppaalpy.classes.simplethings import ConstraintLabel


class ConstraintCache:
    """Class for line based constraint changes.

    (De)serializing with lxml and traversing/creating an Element Tree for
    small updates on constraints is wasteful. Caching updates on constraints
    by creating patches and applying these patches by linewise editing might
    be a faster alternative. However, since the xml file is not actually parsed,
    the implementation requires the file to be formatted properly. Precisely,
    each "leaf" item must be on a separate single line, and each "inner" item
    must have their "start" and "end" on a separate single line:

    example:
    <transition>
        <source ref="id1"/>
        <target ref="id0"/>
        <label kind="guard" x="289" y="-25">x &gt;= 100</label>
    </transition>
    """

    def __init__(self, nta: nta.NTA) -> None:
        """Initialize ConstraintCache.

        Attributes:
            patches: List of ConstraintPatch objects. Those patches are
                "flushed" to an output file when the user choses to do so.
            nta: The parent nta.
        """
        self.patches: List[ConstraintPatch] = []
        self.nta = nta

    def cache(self, patch: "ConstraintPatch") -> None:
        """Store a patch."""
        self.patches.append(patch)

    def _apply_single_patch(self, lines: List[str], patch: "ConstraintPatch") -> None:
        """Apply a single patch."""

        def handle_loc(i: int, loc: n.Location) -> None:
            # Find the line with the relevant location.
            loc_string = '<location id="%s"' % loc.id
            while loc_string not in lines[i]:
                i += 1
            location_line_index = i
            # If no invariant exists for this location in the file,
            # create a new line for the new invariant label. It should be
            # inserted just after the Name label, if it exists, and before
            # all the other labels.
            target_index = location_line_index

            # Find the invariant line, if it exists.
            while True:
                line = lines[i].strip()
                if line.startswith('<name x="'):
                    # Invariant comes after name.
                    target_index = i
                if line.startswith('<label kind="invariant"'):  # Invariant found.
                    target_index = i
                    break
                if line.startswith("</location>"):  # No invariant
                    break
                i += 1

            patch.change.patch_line(lines, target_index, location_line_index)

        def handle_trans(i: int, trans: tr.Transition) -> None:
            # Find the line with the relevant transition.
            trans_index = trans.template.graph._transitions.index(trans)
            curr_trans = -1
            while curr_trans < trans_index:
                if lines[i].strip().startswith("<transition>"):
                    curr_trans += 1
                i += 1
            transition_line_index = i - 1
            # If no guard exists for this tranisiton in the file,
            # create a new line for the new guard label. It should be
            # inserted just after the Name label, if one exists, and before
            # all the other labels.
            target_index = transition_line_index + 2  # skip source and target lines

            # Find the guard line, if it exists.
            while True:
                line = lines[i].strip()
                if line.startswith('<label kind="select"'):
                    # Guard comes after select.
                    target_index = i
                if line.startswith('<label kind="guard"'):  # Guard found.
                    target_index = i
                    break
                if line.startswith("</transition>"):  # No invariant
                    break
                i += 1

            patch.change.patch_line(lines, target_index, transition_line_index)

        template_index = self.nta.templates.index(patch.template_ref)
        i = 0
        curr_template_i = -1

        # Find the line the template starts.
        while curr_template_i < template_index:
            if lines[i].strip().startswith("<template>"):
                curr_template_i += 1
            i += 1

        # Check whether the change is on a location or a transition.
        if type(patch.obj_ref) == n.Location:
            handle_loc(i, cast(n.Location, patch.obj_ref))

        else:
            handle_trans(i, cast(tr.Transition, patch.obj_ref))

    def apply_patches(self, lines: List[str]):
        """Given a list of lines, apply changes the list."""
        for patch in self.patches:
            self._apply_single_patch(lines, patch)


class ConstraintPatch:
    """Class for capturing a change on guards and invariants.

    Currently insertion, removal, and update operations on clock constraint
    expressions are supported.
    """

    def __init__(
        self,
        template_ref: te.Template,
        change: "ConstraintChange",
        obj_ref: Union[n.Location, tr.Transition],
    ) -> None:
        """Initialize ConstraintPatch.

        obj_ref argument can be used for initializing the patch

        Args:
            template_ref: The parent template.
            change: A ConstraintChange object.
            location_ref: The parent location.
            transition_ref: The parent transition.
        """
        self.template_ref = template_ref
        self.change = change
        self.obj_ref = obj_ref


class ConstraintChange(metaclass=ABCMeta):
    """Base class for the three operations on constraint changes.

    Attributes:
        constraint: A ClockConstraintExpression object.
    """

    def __init__(self, constraint: ClockConstraintExpression) -> None:
        """Initialize class with the clock constraint expr to be changed."""
        self.constraint = constraint

    @abstractmethod
    def patch_line(self, lines: List[str], index: int, parent_index: int = -1) -> None:
        """Patch a list of lines."""
        pass


class ConstraintRemove(ConstraintChange):
    """Class for keeping track of a constraint removal."""

    def __init__(
        self, constraint: ClockConstraintExpression, remove_label: bool = False
    ) -> None:
        """Create ConstraintRemove given a simple constraint to remove."""
        super().__init__(constraint)
        self.remove_label = remove_label

    def patch_line(self, lines: List[str], index: int, parent_index: int = -1) -> None:
        """Remove a constraint by editing or deleting a line.

        Args:
            lines: List of strings for each line.
            index: Integer index of the current line. If self.remove_constraint
                is False, current line is edited. Otherwise, the line is
                deleted.
            parent_index: Not used.
        """
        parent_index  # for ignoring unused hint.
        if self.remove_label:
            lines.pop(index)

        else:
            # Edit the current line.
            constraint_line = lines[index]
            start = constraint_line.index(">") + 1  # '>' in ...y="..">
            end = constraint_line.index("<", start)  # '<' in </label>
            constraints = constraint_line[start:end].split(" &amp;&amp; ")
            constraints.pop(self._find_matching_constraint(constraints))
            lines[index] = (
                constraint_line[:start]
                + " &amp;&amp; ".join(constraints)
                + constraint_line[end:]
            )

    def _find_matching_constraint(self, constraints: List[str]) -> int:
        """Find the index of the constraint to be deleted.

        Each string is compared with the constraint to be removed.
        """
        comparison_string = self.constraint.to_string(escape=True).replace(" ", "")

        for i, c in enumerate(constraints):
            if c.replace(" ", "") == comparison_string:
                return i

        raise Exception(
            "{comp} does not match with any of the {lst}".format(
                comp=comparison_string, lst=constraints
            )
        )


class ConstraintInsert(ConstraintChange):
    """Class for keeping track of a constraint insertion."""

    def __init__(
        self,
        constraint: ClockConstraintExpression,
        newly_created: Optional[ConstraintLabel] = None,
    ) -> None:
        """Create ConstraintInsert given a simple constraint to insert.

        If a new guard/invariant is created, self.newly_created is set to the
        newly created object. Otherwise, it is None.
        """
        super().__init__(constraint)
        self.newly_created = newly_created

    def patch_line(self, lines: List[str], index: int, parent_index: int) -> None:
        """Insert a constraint by editing or inserting a line.

        Args:
            lines: List of strings for each line.
            index: Integer index of the current line. If self.created_new is
                not none, a new line after the current line is inserted for the
                new invariant/guard label. Otherwise, the new constraint is inserted
                to the current line.
            parent_index: Integer index of the parent transition/location.
                Used for indentation while inserting a new line.
        """
        if self.newly_created is not None:
            # Insert new line after the current line.
            tabs = lines[parent_index].index("<") + 1
            string = (
                tabs * "\t"
                + '<label kind="{kind}" x="{x}" y="{y}">{text}</label>\n'.format(
                    kind=self.newly_created.kind,
                    x=str(self.newly_created.pos[0]),
                    y=str(self.newly_created.pos[1]),
                    text=self.constraint.to_string(escape=True),
                )
            )
            lines.insert(index + 1, string)

        else:
            # Edit the current line.
            constraint_line = lines[index]
            start = constraint_line.index(">") + 1  # '>' in ...y="..">
            insertion_point = constraint_line.index("<", start)  # '<' in </label>
            edited_line = "{prev} &amp;&amp; {text}{rest}".format(
                prev=constraint_line[:insertion_point],
                text=self.constraint.to_string(escape=True),
                rest=constraint_line[insertion_point:],
            )
            lines[index] = edited_line


class ConstraintUpdate(ConstraintChange):
    """Class for keeping track of a constraint update."""

    def __init__(
        self, constraint: ClockConstraintExpression, new_threshold: str
    ) -> None:
        """Initialize class with the new and the old thresholds."""
        super().__init__(constraint)
        self.old = constraint.threshold
        self.new = new_threshold

    def patch_line(self, lines: List[str], index: int, parent_index: int = -1) -> None:
        """Update a constraint by editing a line.

        Args:
            lines: List of strings for each line.
            index: Integer index of the current line.
            parent_index: Not used.
        """
        parent_index
        constraint_line = lines[index]
        start = constraint_line.index(">") + 1  # '>' in ...y="..">
        end = constraint_line.index("<", start)  # '<' in </label>
        constraints = constraint_line[start:end].split(" &amp;&amp; ")
        update_index = self._find_matching_constraint(constraints)
        constraints[update_index] = constraints[update_index].replace(
            self.old, self.new
        )
        lines[index] = (
            constraint_line[:start]
            + " &amp;&amp; ".join(constraints)
            + constraint_line[end:]
        )

    def _find_matching_constraint(self, constraints: List[str]) -> int:
        """Find the index of the constraint to be updated.

        Each string is compared with the constraint to be updated.
        """
        # Get the old comparison string.
        comparison_string = (
            self.constraint.to_string(escape=True)
            .replace(" ", "")
            .replace(self.constraint.threshold, self.old)
        )

        for i, c in enumerate(constraints):
            if c.replace(" ", "") == comparison_string:
                return i

        raise Exception(
            "{comp} does not match with any of the {lst}".format(
                comp=comparison_string, lst=constraints
            )
        )

    def generate_new_constraint(self) -> ClockConstraintExpression:
        """Create a copy ClockConstraintExpression with the updated threshold."""
        res = copy(self.constraint)
        res.threshold = self.new
        return res
