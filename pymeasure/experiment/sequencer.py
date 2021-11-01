#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import logging, re, numpy
from itertools import product

from logging import Handler

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SequenceEvaluationException(Exception):
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
        return "{} \"{}\" \"{}\"".format("-"*(self.level + 1), self.parameter, self.expression)

class SequenceFileHandler():
    """ Represent a sequence file and its methods

    A sequence file is a text file which represent a tree structure.
    Each node of the tree is composed of 3 elements:

    - Level: that is the distance from the root node
    - Parameter: A string that is the parameter name
    - Expression: A python expression which describe the list of values to be assumed by the Parameter.
    The syntax of the file is as follow:

    - "Parameter1" "(1,2,3)"
    -- "Parameter2" "(4,5,6)"
    --- "Parameter3" "(6,7,8)"
    - "Parameter4" "range(1,3)"

    In this case, the tree is composed of a root node with two children (Parameter1 and Parameter4)
    Parameter2 is the only child of Parameter1 and Parameter3 is the only child of Parameter2.
    Parameter4 has no child.
    [Add grphical representation ???]
 """

    MAXDEPTH = 10
    SAFE_FUNCTIONS = {
        'range': range,
        'sorted': sorted,
        'list': list,
        'arange': numpy.arange,
        'linspace': numpy.linspace,
        'arccos': numpy.arccos,
        'arcsin': numpy.arcsin,
        'arctan': numpy.arctan,
        'arctan2': numpy.arctan2,
        'ceil': numpy.ceil,
        'cos': numpy.cos,
        'cosh': numpy.cosh,
        'degrees': numpy.degrees,
        'e': numpy.e,
        'exp': numpy.exp,
        'fabs': numpy.fabs,
        'floor': numpy.floor,
        'fmod': numpy.fmod,
        'frexp': numpy.frexp,
        'hypot': numpy.hypot,
        'ldexp': numpy.ldexp,
        'log': numpy.log,
        'log10': numpy.log10,
        'modf': numpy.modf,
        'pi': numpy.pi,
        'power': numpy.power,
        'radians': numpy.radians,
        'sin': numpy.sin,
        'sinh': numpy.sinh,
        'sqrt': numpy.sqrt,
        'tan': numpy.tan,
        'tanh': numpy.tanh,
    }
    def __init__ (self, file_obj):
        self.file_obj = file_obj
        self._sequences = None
        self.parse()

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
                    string, {"__builtins__": None}, SequenceFileHandler.SAFE_FUNCTIONS
                )
            except TypeError:
                if log_enabled:
                    log.error("TypeError, likely a typo in one of the " +
                              "functions for parameter '{}', depth {}".format(
                                  name, depth
                              ))
                raise SequenceEvaluationException("TypeError, likely a typo")
            except SyntaxError:
                if log_enabled:
                    log.error("SyntaxError, likely unbalanced brackets " +
                              "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationException("SyntaxError, likely unbalanced brackets")
            except ValueError:
                if log_enabled:
                    log.error("ValueError, likely wrong function argument " +
                              "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationException("ValueError, likely wrong function argument")
            except Exception as e:
                raise SequenceEvaluationException(e)
        else:
            if log_enabled:
                log.error("No sequence entered for " +
                          "for parameter '{}', depth {}".format(name, depth))
            raise SequenceEvaluationException("No sequence entered")

        evaluated_string = numpy.array(evaluated_string)
        return evaluated_string

    @property
    def sequences(self):
        """ Return a list of sequences, each one representing a node of the tree """
        if self._sequences is None:
            raise Exception("Not initialized")
        return self._sequences

    def _get_idx(self, seq_item):
        """ Return the index of the list whose value correspond to sequence """
        try:
            idx = self._sequences.index(seq_item)
        except:
            idx = -1 # Sequence not found, assuming idenx does not exist

        if idx < 0:
            level = -1
        else:
            level = self[idx].level

        return idx, level

    def add_node(self, name, parent_seq_item=None):
        """ Add a node under this parent identified by parent_sequence """
        parent_idx, level = self._get_idx(parent_seq_item)
        
        seq_item = SequenceItem(level+1,
                                name,
                                "",
                                parent_seq_item)
        # Find position where to insert new row
        idx = parent_idx + 1
        while idx < len(self):
            if self[idx].level <= level:
                break
            idx += 1

        self._sequences.insert(idx, seq_item)
        # Update parent dictionary
        for node in range(len(self._sequences) - 1, idx, -1):
            self.parent[node] = self.parent[node-1]
            
        self.parent[idx] = parent_idx
        return seq_item, self.get_children_order(seq_item)
    
    def remove_node(self, seq_item):
        """ Remove node identified by seq_item """
        # if node identified by idx has children, we need to remove them first
        for child_seq_item in self.children(seq_item):
            self.remove_node(child_seq_item)
        
        idx, level = self._get_idx(seq_item)
        parent_idx = self.parent[idx]

        self._sequences.remove(seq_item)
        # Update parent dictionary
        for node in range(idx, len(self._sequences)):
            new_node = self.parent[node+1]
            new_node = new_node if new_node < idx else new_node - 1
            self.parent[node] = new_node

        del self.parent[len(self._sequences)]

        if parent_idx == -1:
            parent_seq_item = None
        else:
            parent_seq_item = self[parent_idx]

        return parent_seq_item, self.get_children_order(parent_seq_item)
        
    def children(self, seq_item):
        """ return a list of children of node identified by seq_item """
        idx, current_level = self._get_idx(seq_item)
        child_list = []
        idx += 1
        while idx < len(self):
            if self[idx].level == (current_level + 1):
                child_list.append(self[idx])
            if self[idx].level <= current_level:
                break
            idx += 1
        return child_list
        
    def get_children(self, seq_item, index):
        """ Return the children of order index of the node in row """

        child_list = self.children(seq_item)

        if index >= len(child_list):
            child = None
        else:
            child = child_list[index]
        return child

    def get_children_order(self, seq_item):
        """ Return the children of order of the node identified by seq_item

        The children order is the index related to the parent's children list.

        Provide example here: TODO
        """

        if seq_item is None:
            return -1
        idx, _ = self._get_idx(seq_item)
        # Get parent
        parent_idx = self.parent[idx] if idx >= 0 else -1
        parent_seq_item = None if parent_idx < 0 else self.sequences[parent_idx]

        # Get parent's children list
        children_list = self.children(parent_seq_item)

        return children_list.index(seq_item)

    def get_parent(self, seq_item):
        """ Return parent of node identified by seq_item """
        idx, _ = self._get_idx(seq_item)

        parent_idx = self.parent[idx] if idx >= 0 else -1
        parent_seq_item = None if parent_idx < 0 else self.sequences[parent_idx]

        return parent_seq_item, self.get_children_order(parent_seq_item)

    def set_data(self, seq_item, row, column, value):
        """ Set data for node identified by seq_item """
        
        idx, _ = self._get_idx(seq_item)

        if idx < 0:
            return False

        self.sequences[idx][column] = value
        return True

    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, key):
        return self.sequences[key]

    def parse(self):
        """
        Read and parse a sequence file.

        """

        self._sequences = []
        self.parent = {}
        current_parent = -1
        current_level = -1
        current_row = -1

        pattern = re.compile("([-]+) \"(.*?)\", \"(.*?)\"")
        self.file_obj.seek(0)
        for line in self.file_obj:
            line = line.strip()
            match = pattern.search(line)

            if not match:
                continue

            level = len(match.group(1)) - 1

            if level < 0:
                continue

            parameter = match.group(2)
            sequence = match.group(3)
            if level == (current_level + 1):
                self.parent[current_row + 1] = current_parent
                current_parent = current_row + 1
                current_level = current_level + 1
            elif (level <= current_level):
                # Find parent
                current_parent -= 1
                while current_parent >= 0:
                    current_level = self._sequences[current_parent].level
                    if level == (current_level + 1):
                        break
                    current_parent -= 1
                if current_parent == -1:
                    current_level = -1
                self.parent[current_row+1] = current_parent
                current_parent = current_row + 1
                current_level = current_level + 1
            else:
                raise Exception("Invalid file format: level missing ?")
            parent = None
            parent_index = self.parent[current_row + 1]
            if parent_index >= 0:
                parent = self._sequences[parent_index]

            data = SequenceItem(level,
                                parameter,
                                sequence,
                                parent)
            
            self._sequences.append(data)
            current_row += 1

    def save(self, filename=None):
        """ Save modified sequence to file """
        for item in self.sequences:
            print(str(item))

    def parameters_sequence(self, names_map=None):
        """
        Generate a list of parameters from the sequence tree.

        :param names_map: an optional dict to map paramter name
        :return: A list of dictionaries. Each dictionary represents a parameters setting
        for running an experiment.
        """

        sequences = []
        current_sequence = [[] for i in range(self.MAXDEPTH)]
        temp_sequence = [[] for i in range(self.MAXDEPTH)]

        idx = 0
        while (idx < len(self._sequences)):
            depth, parameter, seq = self[idx].level, self[idx].parameter, self[idx].expression
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

if __name__ == "__main__":
    import sys

    fd = open(sys.argv[1])
    names_map = {
        "Delay Time": "delay",
        "Random Seed": "seed",
        "Loop Iterations" : "iterations",
    }
    s=SequenceFileHandler(fd)
    print (s.parameters_sequence(names_map))
    print (s.sequences)
    print (s[2])
    
