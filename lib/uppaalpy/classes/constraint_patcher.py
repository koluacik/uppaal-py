"""Class definitions for fast constraint changes."""


class ConstraintCache:
    """Class for line based constraint changes.

    (De)serializing with lxml and traversing/creating an Element Tree for
    small updates on constraints is wasteful. Caching updates on constraints
    by creating patches and applying these patches by linewise editing might
    be a faster alternative. However, since the xml file is not actually parsed,
    the implementation requires the file to be formatted properly. Namely,
    each "leaf" item must be on a separate single line, and each "inner" item
    must have their "start" and "end" on a separate single line:

    ex:
    <transition>
        <source ref="id1"/>
        <target ref="id0"/>
        <label kind="guard" x="289" y="-25">x &gt;= 100</label>
    </transition>
    """

    def __init__(self, nta):
        """Initialize ConstraintCache.

        Attributes:
            patches: List of ConstraintPatch objects. Those patches are
                "flushed" to an output file when the user choses to do so.
            nta: The parent nta.
        """
        self.patches = []
        self.nta = nta

    def cache(self, patch):
        """Store a patch."""
        self.patches.append(patch)

    def _apply_single_patch(self, lines, patch):
        """Apply a single patch."""

        def handle_loc(i, loc):
            # Find the line with the relevant location.
            loc_string = '<template id="%s"' % loc.id
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
                if line.startswith('<label kind="name"'):
                    target_index = i
                if line.startswith('<label kind="invariant"'):  # Invariant found.
                    target_index = i
                    break
                if line.startswith("</location>"):  # No invariant
                    break
                i += 1

            patch.change.patch_line(lines, target_index, location_line_index)

        def handle_trans(i, trans):
            # Find the line with the relevant transition.
            trans_index = trans.template.graph._transitions.index(
                patch.transition_ref
            )
            curr_trans = -1
            while curr_trans < trans_index:
                if lines[i].strip().startswith("<transition>"):
                    curr_trans += 1
                i += 1
            transition_line_index = i
            # If no guard exists for this tranisiton in the file,
            # create a new line for the new guard label. It should be
            # inserted just after the Name label, if one exists, and before
            # all the other labels.
            target_index = transition_line_index

            # Find the guard line, if it exists.
            while True:
                line = lines[i].strip()
                if line.startswith('<label kind="name"'):
                    target_index = i
                if line.startswith('<label kind="guard"'):  # Guard found.
                    target_index = i
                    break
                if line.startswith("</location>"):  # No invariant
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
        if patch.location_ref is not None:
            handle_loc(i, patch.location_ref)

        else:
            handle_trans(i, patch.transition_ref)

    def apply_patches(self, lines):
        """Given a list of lines, apply changes the list."""
        for patch in self.patches:
            self._apply_single_patch(lines, patch)


class ConstraintPatch:
    """Class for capturing a change on a guard and location."""

    def __init__(self, template_ref, change, location_ref=None, transition_ref=None):
        """Initialize ConstraintPatch.

        Args:
            template_ref: The parent template.
            change: A ConstraintChange object.
            location_ref: The parent location.
            transition_ref: The parent transition.
        """
        self.template_ref = template_ref  # kwargs["template"]
        self.location_ref = location_ref  # kwargs.get("location")
        self.transition_ref = transition_ref  # kwargs.get("transition")
        self.change = change  # kwargs["change"]


class ConstraintChange:
    """Base class for the three operations on constraint changes.

    Attributes:
        constraint: A SimpleConstraint.
    """

    def __init__(self, constraint):
        """Initialize class with the simple constraint to be changed."""
        self.constraint = constraint


class ConstraintRemove(ConstraintChange):
    """Class for keeping track of a constraint removal."""

    def __init__(self, constraint, remove_constraint=False):
        """Create ConstraintRemove given a simple constraint to remove."""
        super().__init__(constraint)
        self.remove_constraint = remove_constraint

    def patch_line(self, lines, index, parent_index=-1):
        """Remove a constraint by editing or deleting a line.

        Args:
            lines: List of strings for each line.
            index: Integer index of the current line. If self.remove_constraint
                is False, current line is edited. Otherwise, the line is
                deleted.
            parent_index: Not used.
        """
        if self.remove_constraint:
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
            print("st", constraint_line[:start])
            print("mi", " &amp;&amp; ".join(constraints))
            print("en", constraint_line[end:])

    def _find_matching_constraint(self, constraints):
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

    def __init__(self, constraint, newly_created=None):
        """Create ConstraintInsert given a simple constraint to insert.

        If a new guard/invariant is created, self.newly_created is set to the
        newly created object. Otherwise, it is None.
        """
        super().__init__(constraint)
        self.newly_created = newly_created

    def patch_line(self, lines, index, parent_index):
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
                + '<label kind="{kind}" x="{x}" y="{y}">{text}</label>'.format(
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

    def __init__(self, constraint, old_threshold, new_threshold):
        """Initialize class with the new and the old thresholds."""
        super().__init__(constraint)
        self.old = old_threshold
        self.new = new_threshold

    def patch_line(self, lines, index, parent_index=-1):
        """Update a constraint by editing a line.

        Args:
            lines: List of strings for each line.
            index: Integer index of the current line.
            parent_index: Not used.
        """
        constraint_line = lines[index]
        start = constraint_line.index(">") + 1  # '>' in ...y="..">
        end = constraint_line.index(">", start)  # '<' in </label>
        constraints = constraint_line[start:end].split(" &amp;&amp; ")
        update_index = self._find_matching_constraint(constraints)
        constraints[update_index] = constraints[update_index].replace(
            str(self.old), str(self.new)
        )
        lines[index] = (
            constraint_line[:start]
            + " &amp;&amp; ".join(constraints)
            + constraint_line[end:]
        )

    def _find_matching_constraint(self, constraints):
        """Find the index of the constraint to be deleted.

        Each string is compared with the constraint to be updated.
        """
        # Get the old comparison string of
        comparison_string = (
            self.constraint.to_string(escape=True)
            .replace(" ", "")
            .replace(str(self.new), str(self.old))
        )

        for i, c in enumerate(constraints):
            if c.replace(" ", "") == comparison_string:
                return i

        raise Exception(
            "{comp} does not match with any of the {lst}".format(
                comp=comparison_string, lst=constraints
            )
        )
