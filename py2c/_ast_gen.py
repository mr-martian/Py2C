#!/usr/bin/python3
"""AST nodes file generator

This file generates the ast that we use as the meduim to translate Python code.
It makes it possible to translate Python code to C code without multiple AST
systems.
"""

#-------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


import os
import re
import collections
from textwrap import dedent

import ply.lex
import ply.yacc

_PREFIX = dedent("""
""").strip()


#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class ParserError(Exception):
    """Errors raised by the Parser while Parsing
    """


#-------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------
def remove_comments(text):
    """Removes all text after a '#' in all lines of the text
    """
    return re.sub(r"(?m)\#.*($|\n)", "", text)


def _prettify_list(li):
    """
    """
    if li == []:
        return "[]"
    else:
        lines = ["["]
        for name, type_, modifier in li:
            lines.append(
                " "*8 + "({!r}, {}, {}),".format(name, type_, modifier)
            )
        lines.append(" "*4 + "]")

        return "\n".join(lines)


Node = collections.namedtuple("Node", "name parent attrs")


#-------------------------------------------------------------------------------
# Parsing of AST nodes declaration
#-------------------------------------------------------------------------------
class Parser(object):
    """Parses the definitions in the definition files
    """
    def __init__(self):
        super(Parser, self).__init__()
        self.tokens = ("NAME",)
        self.literals = "()[]:*?+,"

        # Tokens for lexer
        self.t_NAME = r"\w+"
        self.t_ignore = " \t"

        self._lexer = ply.lex.lex(module=self)
        self._parser = ply.yacc.yacc(module=self, start="start")

    def parse(self, text):
        """Parses the definition text into a data representaton of it.
        """
        text = remove_comments(text)
        return self._parser.parse(text, lexer=self._lexer)

    def t_newline(self, t):
        r"\n"
        t.lexer.lineno += 1

    def p_error(self, t):
        raise ParserError("Unexpected token: " + str(t))

    def t_error(self, t):
        raise ParserError("Unable to tokenize" + t.value)

    #---------------------------------------------------------------------------
    # Parsing
    #---------------------------------------------------------------------------
    def p_empty(self, p):
        "empty : "

    def p_start(self, p):
        "start : zero_or_more_declaration"
        p[0] = p[1]

    def p_zero_or_more_declaration(self, p):
        """zero_or_more_declaration : zero_or_more_declaration declaration
                                    | empty
        """
        if len(p) == 2:
            p[0] = ()
        else:
            p[0] = p[1] + (p[2],)

    def p_declaration(self, p):
        "declaration : NAME parent_class_opt ':' '[' attr_list ']'"
        name, attrs = (p[1], p[5])
        # Check for duplicates
        seen = []
        duplicated = []
        for field_name, _, _ in attrs:
            if field_name in seen:
                duplicated.append(field_name)
            else:
                seen.append(field_name)

        if duplicated:
            msg = "Multiple declarations in {!r} of attribute{} {!r}".format(
                name,
                "s" if len(duplicated) > 1 else "",
                ", ".join(duplicated)
            )
            raise ParserError(msg)
        else:
            p[0] = Node(p[1], p[2], p[5])

    def p_parent_class_opt(self, p):
        """parent_class_opt : '(' NAME ')'
                            | empty
        """
        if len(p) > 2:
            p[0] = p[2]
        else:
            p[0] = None

    def p_attr_list_1(self, p):
        """attr_list : attr more_attrs_maybe ','
                     | attr more_attrs_maybe
                     | empty
        """
        if len(p) > 2:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_more_attrs_maybe(self, p):
        """more_attrs_maybe : more_attrs_maybe ',' attr
                            | empty
        """
        if len(p) > 2:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = []

    def p_attr(self, p):
        "attr : NAME modifier NAME"
        p[0] = (p[3], p[1], p[2])

    def p_modifier(self, p):
        """modifier : empty
                    | '?'
                    | '+'
                    | '*'
        """
        if p[1] == "+":
            p[0] = "ONE_OR_MORE"
        elif p[1] == "*":
            p[0] = "ZERO_OR_MORE"
        elif p[1] == "?":
            p[0] = "OPTIONAL"
        else:
            p[0] = "NEEDED"


#-------------------------------------------------------------------------------
# Generation of sources for AST nodes class
#-------------------------------------------------------------------------------
class SourceGenerator(object):
    """Generates the code from the Parser's parsed data
    """
    def __init__(self):
        super(SourceGenerator, self).__init__()

    def generate_sources(self, data):
        """Generates source code from the data generated by :py:class:`Parser`
        """
        classes = []
        for node in data:
            classes.append(self._translate_node(node))
        # Join classes and ensure newline at EOF
        return "\n\n\n".join(classes) + "\n"

    def _translate_node(self, node):
        name = node.name

        if node.parent is None:
            parent = "object"
            field_text = _prettify_list(node.attrs)
        else:
            parent = node.parent
            field_text = parent + "._fields"
            if node.attrs:
                field_text += " + " + _prettify_list(node.attrs)

        return dedent("""
            class {0}({1}):
                _fields = {2}
        """).strip().format(name, parent, field_text)


# API for dual_ast
def generate(base_dir, files_to_convert):
    """Generate sources for the AST nodes definition files provided
    """
    content = []
    for fname in files_to_convert:
        with open(os.path.join(base_dir, fname)) as f:
            content.append(f.read())

    text = "\n\n".join(content)

    parser = Parser()
    src_gen = SourceGenerator()

    return src_gen.generate_sources(parser.parse(text))


if __name__ == '__main__':
    print(generate(".", ["python.ast"]))
