#!/usr/bin/env python

import ast
from collections import defaultdict
import c_ast
c_ast.prepare()

__all__ = ["ASTTranslator", "c_ast", "ast", "defaultdict", "get_C_AST"]



def in_scope(obj, scope_dict, curr_scope):
    for i in range(curr_scope+1):
        if obj in scope_dict[i]:
            return True
    return False

class ASTTranslator(ast.NodeVisitor):
    """Translates Python AST into C AST

    This is a NodeVisitor that visits the Python AST validates it for conversion
    and creates another AST, for C code (with type definitions and other stuff),
    from which C code is generated.

    Attributes:
        errors: A list that contains the error-messages that of errors that
                occurred during translation
        functions: A list holding function names

    """
    def __init__(self):
        super(ASTTranslator, self).__init__()
        self.setup()

    def setup(self):
        self.errors = []

    # Errors
    def log_error(self, msg, node=None):
        if hasattr(node, "lineno"):
            msg = "Line ({0}): ".format(node.lineno) + msg
        self.errors.append(msg)

    def print_errors(self):
        for msg in self.errors:
            print "ERROR: "+msg
        print "-"*80

    def get_node(self, node):
        """Get the C AST from the Python AST `node`
        Args:
            node: The Python AST to be converted to C AST
        Returns:
            A C node, from the c_ast.py
        Raises:
            Exception: If the AST could not be converted, due to some error
                       Raised after printing those errors.
        """
        self.setup()
        retval = self.visit(node)
        if self.errors:
            self.print_errors()
            raise Exception("Problems with Node provided.")
        else:
            return retval

    # Modified to return values
    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                li = []
                for item in value:
                    if isinstance(item, ast.AST):
                        li.append(self.visit(item))
                return li
            elif isinstance(value, ast.AST):
                return self.visit(value)

    def body(self, body):
        return map(self.visit, body)

    def visit_Module(self, node):
        return c_ast.Module(self.body(node.body))

    def visit_Print(self, node, py3=False):
        if py3: # python 3 print function
            keywords = {}
            if node.keywords is not None:
                for kw in node.keywords:
                    keywords[kw.arg] = kw.value

            sep = keywords.get('sep', ast.Str(' ')).s
            end = keywords.get('end', ast.Str('\n')).s
            dest = keywords.get('file', None)
            if dest is not None:
                dest = self.visit(dest)
            values = map(self.visit, node.args)
        else:
            sep = ' '
            end = '\n' if node.nl else ' '
            dest = node.dest
            if dest is not None:
                dest = self.visit(dest)
            values = map(self.visit, node.values)

        return c_ast.Print(dest=dest, values=values, sep=sep, end=end)

    def visit_Call(self, node):
        if node.func.id == 'print': # Python 3 print
            return self.visit_Print(node, True)

        if node.keywords:
            self.log_error("Calls with keyword arguments not supported", node)
        if node.starargs is not None or node.kwargs is not None:
            self.log_error("Calls with starred arguments not supported", node)
        func = self.visit(node.func)
        args = map(self.visit, node.args)
        return c_ast.Call(func=func, args=args)

    def visit_Num(self, node):
        if isinstance(node.n, int):
            return c_ast.Int(n=node.n)
        elif isinstance(node.n, float):
            return c_ast.Float(n=node.n)
        else:
            msg = "Only ints and floats supported, {0} numbers not supported"
            raise ValueError(msg.format(node.n.__class__.__name__))

    def visit_Name(self, node):
        return c_ast.Name(id=node.id)

    def visit_Str(self, node):
        return c_ast.Str(s=node.s)


def get_C_AST(py_ast):
    """Translate Python AST in C AST"""
    translator = ASTTranslator()
    try:
        return translator.visit(py_ast)
    except Exception as e:
        print vars(e)

def main():
    text = 'print a(1, 1.0, "a")'
    node = ast.parse(text)
    print ast.dump(node)
    t = ASTTranslator()
    print t.get_node(node)


if __name__ == '__main__':
    main()
