#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import re
from itertools import product

import numpy as np

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SequenceEvaluationError(Exception):
    """Raised when the evaluation of a sequence string goes wrong."""
    pass


class SequenceItem(object):
    """ Class representing a sequence row """
    column_map = {
        0: "level",
        1: "parameter",
        2: "expression",
    }

    def __init__(self, level, parameter, expression, parent):
        self.level = level
        self.parameter = parameter
        self.expression = expression
        self.parent = parent

    def __getitem__(self, idx):
        if idx in self.column_map:
            return getattr(self, self.column_map[idx])
        else:
            return super().__getitem__(idx)

    def __setitem__(self, idx, value):
        if idx in self.column_map:
            return setattr(self, self.column_map[idx], value)
        else:
            return super().__setitem__(idx, value)

    def __str__(self):
        return "{} \"{}\", \"{}\"".format("-" * (self.level + 1), self.parameter, self.expression)


class SequenceHandler:
    """ It represents a sequence, that is a tree of parameter sweep.

    A sequence can be loaded from a file or created programmatically with :meth:`~.add_node`
    and :meth:`~.remove_node`

    The internal representation is a nodes tree with each node composed of 3 elements:

    - Level: that is the distance from the root node
    - Parameter: A string that is the parameter name
    - Expression: A python expression which describes the list of values to be assumed
      by the Parameter.

    The syntax of the file is as follow: ::

    - "Parameter1", "(1,2,3)"
    -- "Parameter2", "(4,5,6)"
    --- "Parameter3", "(6,7,8)"
    - "Parameter4", "range(1,3)"

    In this case, the tree is composed of a root node with two children (Parameter1 and Parameter4)
    Parameter2 is the only child of Parameter1 and Parameter3 is the only child of Parameter2.
    Parameter4 has no child.

    Data is stored internally as a list where each
    item matches a row of the sequence file.

    Data can also be saved back to the file object provided.
 """

    MAXDEPTH = 10
    SAFE_FUNCTIONS = {
        'range': range,
        'sorted': sorted,
        'list': list,
        'arange': np.arange,
        'linspace': np.linspace,
        'arccos': np.arccos,
        'arcsin': np.arcsin,
        'arctan': np.arctan,
        'arctan2': np.arctan2,
        'ceil': np.ceil,
        'cos': np.cos,
        'cosh': np.cosh,
        'degrees': np.degrees,
        'e': np.e,
        'exp': np.exp,
        'fabs': np.fabs,
        'floor': np.floor,
        'fmod': np.fmod,
        'frexp': np.frexp,
        'hypot': np.hypot,
        'ldexp': np.ldexp,
        'log': np.log,
        'log10': np.log10,
        'modf': np.modf,
        'pi': np.pi,
        'power': np.power,
        'radians': np.radians,
        'sin': np.sin,
        'sinh': np.sinh,
        'sqrt': np.sqrt,
        'tan': np.tan,
        'tanh': np.tanh,
    }

    def __init__(self, valid_inputs=(), file_obj=None):
        self._sequences = []
        self.valid_inputs = valid_inputs
        if file_obj:
            self.load(file_obj)

    @staticmethod
    def eval_string(string, name=None, depth=None, log_enabled=True):
        """
        Evaluate the given string. The string is evaluated using a list of
        pre-defined functions that are deemed safe to use, to prevent the
        execution of malicious code. For this purpose, also any built-in
        functions or global variables are not available.

        :param string: String to be interpreted.
        :param name: Name of the to-be-interpreted string, only used for
            error messages.
        :param depth: Depth of the to-be-interpreted string, only used
            for error messages.
        :param log_enabled: Enable log messages.
        """

        evaluated_string = None
        if len(string) > 0:
            try:
                evaluated_string = eval(
                    string, {"__builtins__": None}, SequenceHandler.SAFE_FUNCTIONS
                )
            except TypeError:
                if log_enabled:
                    log.error("TypeError, likely a typo in one of the " +
                              "functions for parameter '{}', depth {}".format(
                                  name, depth
                              ))
                raise SequenceEvaluationError("TypeError, likely a typo")
            except SyntaxError:
                if log_enabled:
                    log.error("SyntaxError, likely unbalanced brackets " +
                              "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationError("SyntaxError, likely unbalanced brackets")
            except ValueError:
                if log_enabled:
                    log.error("ValueError, likely wrong function argument " +
                              "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationError("ValueError, likely wrong function argument")
            except Exception as e:
                raise SequenceEvaluationError(e)
        else:
            if log_enabled:
                log.error("No sequence entered for " +
                          "for parameter '{}', depth {}".format(name, depth))
            raise SequenceEvaluationError("No sequence entered")

        evaluated_string = np.array(evaluated_string)
        return evaluated_string

    def _get_idx(self, seq_item):
        """ Return the index and level of the list whose value correspond to sequence """
        try:
            idx = self._sequences.index(seq_item)
        except ValueError:
            idx = -1  # Sequence not found, assuming idenx does not exist

        if idx < 0:
            level = -1
        else:
            level = self._sequences[idx].level

        return idx, level

    def add_node(self, name, parent_seq_item=None):
        """ Add a node under the parent identified by parent_seq_item """
        parent_idx, level = self._get_idx(parent_seq_item)

        seq_item = SequenceItem(level + 1,
                                name,
                                "",
                                parent_seq_item)
        # Find position where to insert new row
        idx = parent_idx + 1
        while idx < len(self._sequences):
            if self._sequences[idx].level <= level:
                break
            idx += 1

        self._sequences.insert(idx, seq_item)
        return seq_item, self.get_children_order(seq_item)

    def remove_node(self, seq_item):
        """ Remove node identified by seq_item """
        # if node identified by idx has children, we need to remove them first
        for child_seq_item in self.children(seq_item):
            self.remove_node(child_seq_item)

        self._sequences.remove(seq_item)

        return seq_item.parent, self.get_children_order(seq_item.parent)

    def children(self, seq_item):
        """ return a list of children of node identified by seq_item """
        idx, current_level = self._get_idx(seq_item)
        child_list = []
        idx += 1
        while idx < len(self._sequences):
            if self._sequences[idx].level == (current_level + 1):
                child_list.append(self._sequences[idx])
            if self._sequences[idx].level <= current_level:
                break
            idx += 1
        return child_list

    def get_children(self, seq_item, index):
        """ Return the children of order index of the node seq_item """

        child_list = self.children(seq_item)

        if index >= len(child_list):
            child = None
        else:
            child = child_list[index]
        return child

    def get_children_order(self, seq_item):
        """ Return the children order of the node identified by seq_item

        The children order is the index related to the parent's children list.

        :param seq_item: SequenceItem instance or None
        """

        if seq_item is None:
            return -1

        # Get parent's children list
        children_list = self.children(seq_item.parent)

        return children_list.index(seq_item)

    def get_parent(self, seq_item):
        """ Return parent of node identified by seq_item """

        return seq_item.parent, self.get_children_order(seq_item.parent)

    def set_data(self, seq_item, row, column, value):
        """ Set data for node identified by seq_item """

        idx, _ = self._get_idx(seq_item)

        if idx < 0:
            return False

        self._sequences[idx][column] = value
        return True

    def load(self, file_obj, append=False):
        """
        Read and parse a sequence stored in a file.

        :params file_obj: file object
        :params append: flag to control whether to append to or replace current sequence

        """

        _sequences = []
        if append:
            _sequences += self._sequences
        current_parent = None

        pattern = re.compile("([-]+) \"(.*?)\", \"(.*?)\"")
        file_obj.seek(0)
        for line in file_obj:
            line = line.strip()
            match = pattern.search(line)

            if not match:
                continue

            level = len(match.group(1)) - 1

            if level < 0:
                continue

            parameter = match.group(2)
            sequence = match.group(3)
            parent_level = -1 if current_parent is None else current_parent.level
            if level == (parent_level + 1):
                pass
            elif (level <= parent_level):
                # Find parent
                current_parent = current_parent.parent
                while current_parent is not None:
                    if level == (current_parent.level + 1):
                        break
                    current_parent = current_parent.parent
            else:
                raise SequenceEvaluationError("Invalid file format: level missing ?")

            if self.valid_inputs and parameter not in self.valid_inputs:
                error_message = f'Unexpected parameter name "{parameter:s}", ' + \
                    f'valid parameters name are {self.valid_inputs}'
                raise SequenceEvaluationError(error_message)

            data = SequenceItem(level,
                                parameter,
                                sequence,
                                current_parent)
            current_parent = data
            _sequences.append(data)
        # No errors, update internal data
        self._sequences = _sequences

    def save(self, file_obj):
        """ Save modified sequence to file stream

        :param file_obj: file object
        """

        file_obj.write("\n".join(str(item) for item in self._sequences))

    def parameters_sequence(self, names_map=None):
        """
        Generate a list of parameters from the sequence tree.

        :param names_map: an optional dict to map parameter name
        :return: A list of dictionaries. Each dictionary represents a parameters setting
        for running an experiment.
        """

        sequences = []
        current_sequence = [[] for i in range(self.MAXDEPTH)]
        temp_sequence = [[] for i in range(self.MAXDEPTH)]

        idx = 0
        while (idx < len(self._sequences)):
            depth, parameter, seq = self._sequences[idx].level, \
                self._sequences[idx].parameter, \
                self._sequences[idx].expression
            values = self.eval_string(seq, parameter, depth)
            if names_map is not None:
                parameter = names_map[parameter]

            try:
                sequence_entry = [{parameter: value} for value in values]
            except TypeError:
                log.error(
                    "TypeError, likely no sequence for one of the parameters"
                )
            else:
                current_sequence[depth].extend(sequence_entry)

            idx += 1
            next_depth = -1 if idx >= len(self._sequences) else self._sequences[idx].level

            for depth_idx in range(depth, next_depth, -1):
                temp_sequence[depth_idx].extend(current_sequence[depth_idx])

                if depth_idx != 0:
                    sequence_products = list(product(
                        current_sequence[depth_idx - 1],
                        temp_sequence[depth_idx]
                    ))

                    for i in range(len(sequence_products)):
                        try:
                            element = sequence_products[i][1]
                        except IndexError:
                            log.error(
                                "IndexError, likely empty nested parameter"
                            )
                        else:
                            if isinstance(element, tuple):
                                sequence_products[i] = (
                                    sequence_products[i][0], *element)

                    temp_sequence[depth_idx - 1].extend(sequence_products)
                    temp_sequence[depth_idx] = []

                current_sequence[depth_idx] = []
                current_sequence[depth_idx - 1] = []

            if depth == next_depth:
                temp_sequence[depth].extend(current_sequence[depth])
                current_sequence[depth] = []

        sequences = temp_sequence[0]

        for idx in range(len(sequences)):
            if not isinstance(sequences[idx], tuple):
                sequences[idx] = (sequences[idx],)
        return sequences
