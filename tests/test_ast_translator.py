#!/usr/bin/env python

import sys
import ast
import unittest

import support

import py2c.ast_translator as ast_translator
dual_ast = ast_translator.dual_ast


class NodeTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for C AST translation"""
    longMessage = True  # useful!

    def template(self, py_node, expected, msg=""):
        """The template for tests in `NodeTestCase`s"""
        msg = "Improper conversion" + (" of {0}".format(msg) if msg else '')
        c_node = self.get_c_ast(py_node)
        self.assertEqual(c_node, expected, msg=msg)

    def setUp(self):
        self.translator = ast_translator.Py2DualTranslator()

    def get_c_ast(self, py_node):
        self.node = py_node
        return self.translator.visit(self.node)


class ErrorReportingTestCase(unittest.TestCase):
    """Tests for Error Reporting in Py2DualTranslator"""
    def setUp(self):
        self.translator = ast_translator.Py2DualTranslator()

    def test_no_error(self):
        node = ast.Module([])
        self.translator.visit(node)
        self.assertFalse(self.translator.errors)
        try:
            self.translator.get_node(node)
        except Exception:
            self.fail("translator.get_node() raised Exception unexpectedly!", )

    def test_logging_one_error(self):
        node = ast.BinOp(
            op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar")
        )
        self.translator.visit(node)
        self.assertTrue(self.translator.errors)
        # monkey patch print_error to do nothing
        self.translator.print_errors = lambda: None
        self.translator.get_node(node)

    def test_printing_one_error(self):
        node = ast.BinOp(
            op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar")
        )
        self.translator.visit(node)
        self.assertTrue(self.translator.errors)

        # Redirect sys.stdout
        new = support.StringIO()
        old = sys.stdout
        sys.stdout = new

        self.translator.print_errors()
        # restore sys.stdout
        sys.stdout = old
        # get output
        output = new.getvalue()
        new.close()

        # SHould mention the following words
        words = ["error", "translating", "ast"]
        for word in words:
            self.assertIn(word, output.lower())

        self.assertEqual(len(output.splitlines()), 1+1)


#--------------------------------------------------------------------------
# Tests for each Node
#--------------------------------------------------------------------------
class NumTestCase(NodeTestCase):
    """Tests for translation from Num"""

    def test_int_negative(self):
        self.template(ast.Num(-1), dual_ast.Int(-1), "-ve integer")

    def test_int_positive(self):
        self.template(ast.Num(1), dual_ast.Int(1), "+ve integer")

    def test_int_zero(self):
        self.template(ast.Num(0), dual_ast.Int(0), "0 (int)")

    def test_float_negative(self):
        self.template(ast.Num(-1.0), dual_ast.Float(-1.0), "-ve float")

    def test_float_positive(self):
        self.template(ast.Num(1.0), dual_ast.Float(1.0), "+ve float")

    def test_float_zero(self):
        self.template(ast.Num(0.0), dual_ast.Float(0.0), "0 (float)")

    def test_other(self):
        self.template(ast.Num(0j), None)
        self.assertTrue(self.translator.errors)


class StrTestCase(NodeTestCase):
    """Tests for translation from Str"""

    def test_string(self):
        self.template(ast.Str("abc"), dual_ast.Str("abc"))


# TODO : refector names
@unittest.skipUnless(sys.version_info[0] < 3, "Need Python 2 to run")
class Print2TestCase(NodeTestCase):
    """Tests for translation from Print (Python 2)"""

    def test_py2_print1(self):
        """Empty print"""
        # print
        self.template(
            ast.Print(
                values=[],
                dest=None,
                nl=True
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print2(self):
        """Empty print with dest"""
        # print >>foo
        self.template(
            ast.Print(
                values=[],
                dest=ast.Name(id="foo"),
                nl=True
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo"),
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print3(self):
        """Empty print with no newline"""
        # print >> foo,
        self.template(
            ast.Print(
                values=[],
                dest=ast.Name(id="foo"),
                nl=False
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo"),
                sep=' ',
                end=' '
            )
        )

    def test_py2_print4(self):
        """Print with values, dest but no newline"""
        # print >>bar, foo,
        self.template(
            ast.Print(
                values=[ast.Name(id="foo")],
                dest=ast.Name(id="bar"),
                nl=False
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=dual_ast.Name(id="bar"),
                sep=' ',
                end=' '
            )
        )

    def test_py2_print5(self):
        """Print with values, dest, newline"""
        # print >>bar, foo
        self.template(
            ast.Print(
                values=[ast.Name(id="foo")],
                dest=ast.Name(id="bar"),
                nl=True
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=dual_ast.Name(id="bar"),
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print6(self):
        """Print with values, no dest or newline"""
        # print foo,
        self.template(
            ast.Print(
                values=[ast.Name(id="foo")],
                dest=None,
                nl=False
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=None,
                sep=' ',
                end=' '
            )
        )

    def test_py2_print7(self):
        """Print with values and newline but no dest"""
        # print foo
        self.template(
            ast.Print(
                values=[ast.Name(id="foo")],
                dest=None,
                nl=True
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=None,
                sep=' ',
                end='\n'
            )
        )


class Print3TestCase(NodeTestCase):
    """Tests for translation from Print (Python 3)"""

    def test_py3_print_empty(self):
        """Empty print"""
        # print()
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end='\n'
            )
        )

    def test_py3_print_dest(self):
        """Empty print with out-file"""
        # print(file=foo)
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id="foo"))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo"),
                sep=' ',
                end='\n'
            )
        )

    def test_py3_print_no_nl(self):
        """Empty print with no newline"""
        # print(end='')
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[],
                keywords=[
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end=''
            )
        )

    def test_py3_print_dest_no_nl(self):
        """Print with file but no end or value"""
        # print(file=foo, end='')
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id='foo')),
                    ast.keyword(arg='end',  value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo"),
                sep=' ',
                end=''
            )
        )

    def test_py3_print_value_dest_no_nl(self):
        """Print with values, dest but no newline"""
        # print(foo, file=bar, end='')
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[ast.Name(id='foo')],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id='bar')),
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=dual_ast.Name(id="bar"),
                sep=' ',
                end=''
            )
        )

    def test_py3_print_value_dest_nl(self):
        """Print with values, dest, newline"""
        # print(foo, file=bar)
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[ast.Name(id='foo')],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id='bar'))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=dual_ast.Name(id="bar"),
                sep=' ',
                end=''
            )
        )

    def test_py3_print_value_only(self):
        """Print with values, no dest or newline"""
        # print(foo, end='')
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[ast.Name(id='foo')],
                keywords=[
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo")],
                dest=None,
                sep=' ',
                end=''
            )
        )

    def test_py3_print_unexpected_kwd(self):
        """Print with unexpected keyword"""
        # print(foo, incorrect_kwd='')
        self.template(
            ast.Call(
                func=ast.Name(id='print'),
                args=[ast.Name(id='foo')],
                keywords=[
                    ast.keyword(arg='incorrect_kwd', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)


class CallTestCase(NodeTestCase):
    """Tests for translation of Call"""
    def test_call_no_args(self):
        # foo()
        self.template(
            ast.Call(
                func=ast.Name(id='foo'),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Call(
                func=dual_ast.Name(id='foo'),
                args=[]
            )
        )

    def test_call_1_arg(self):
        # foo(bar)
        self.template(
            ast.Call(
                func=ast.Name(id='foo'),
                args=[ast.Name(id='bar')],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Call(
                func=dual_ast.Name(id='foo'),
                args=[dual_ast.Name(id='bar')]
            )
        )

    def test_call_1_kwd(self):
        # foo(unexpected_kwd='')
        self.template(
            ast.Call(
                func=ast.Name(id='foo'),
                args=[],
                keywords=[
                    ast.keyword(arg='unexpected_kwd', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)

    def test_call_starred(self):
        # foo(*starred)
        self.template(
            ast.Call(
                func=ast.Name(id='foo'),
                args=[],
                keywords=[],
                starargs=ast.Name(id='starred'),
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)


class BoolOpTestCase(NodeTestCase):
    """Tests for translation from BoolOp"""

    def test_boolop_and1(self):
        self.template(
            ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Name(id='foo'),
                    ast.Name(id='bar')
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.And(),
                values=[
                    dual_ast.Name(id='foo'),
                    dual_ast.Name(id='bar')
                ]
            )
        )

    def test_boolop_and2(self):
        self.template(
            ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Name(id='foo'),
                    ast.Name(id='bar'),
                    ast.Name(id='baz'),
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.And(),
                values=[
                    dual_ast.Name(id='foo'),
                    dual_ast.Name(id='bar'),
                    dual_ast.Name(id='baz'),
                ]
            )
        )

    def test_boolop_or1(self):
        self.template(
            ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Name(id='foo'),
                    ast.Name(id='bar')
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.Or(),
                values=[
                    dual_ast.Name(id='foo'),
                    dual_ast.Name(id='bar')
                ]
            )
        )

    def test_boolop_or2(self):
        self.template(
            ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Name(id='foo'),
                    ast.Name(id='bar'),
                    ast.Name(id='baz')
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.Or(),
                values=[
                    dual_ast.Name(id='foo'),
                    dual_ast.Name(id='bar'),
                    dual_ast.Name(id='baz')
                ]
            )
        )

    def test_binop_invalid_op(self):
        node = ast.BoolOp(
            op='Blah',
            values=[ast.Name(id="foo"), ast.Name(id="bar")]
        )
        self.assertEqual(self.translator.visit(node), None)


class BinOpTestCase(NodeTestCase):
    """Tests for translation from BinOp"""
    def test_binop_Add(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id='foo'),
                op=ast.Add(),
                right=ast.Name(id='b')
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id='foo'),
                op=dual_ast.Add(),
                right=dual_ast.Name(id='b')
            )
        )

    def test_binop_Sub(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id='foo'),
                op=ast.Sub(),
                right=ast.Name(id='b')
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id='foo'),
                op=dual_ast.Sub(),
                right=dual_ast.Name(id='b')
            )
        )

    def test_binop_Mult(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id='foo'),
                op=ast.Mult(),
                right=ast.Name(id='b')
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id='foo'),
                op=dual_ast.Mult(),
                right=dual_ast.Name(id='b')
            )
        )

    def test_binop_Div(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id='foo'),
                op=ast.Div(),
                right=ast.Name(id='b')
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id='foo'),
                op=dual_ast.Div(),
                right=dual_ast.Name(id='b')
            )
        )

    def test_binop_Mod(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id='foo'),
                op=ast.Mod(),
                right=ast.Name(id='b')
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id='foo'),
                op=dual_ast.Mod(),
                right=dual_ast.Name(id='b')
            )
        )

    def test_binop_invalid_op(self):
        node = ast.BinOp(
            op='Blah',  # Not a valid operator
            left=ast.Name(id="foo"),
            right=ast.Name(id="bar")
        )
        self.assertEqual(self.translator.visit(node), None)
        self.assertTrue(self.translator.errors)


class UnaryOpTestCase(NodeTestCase):
    """Tests for translation from UnaryOp"""
    def test_unary_Not(self):
        self.template(
            ast.UnaryOp(
                op=ast.Not(),
                operand=ast.Name(id='foo')
            ),
            dual_ast.UnaryOp(
                op=dual_ast.Not(),
                operand=dual_ast.Name(id='foo')
            )
        )

    def test_unary_UAdd(self):
        self.template(
            ast.UnaryOp(
                op=ast.UAdd(),
                operand=ast.Name(id='foo')
            ),
            dual_ast.UnaryOp(
                op=dual_ast.UAdd(),
                operand=dual_ast.Name(id='foo')
            )
        )

    def test_unary_USub(self):
        self.template(
            ast.UnaryOp(
                op=ast.USub(),
                operand=ast.Name(id='foo')
            ),
            dual_ast.UnaryOp(
                op=dual_ast.USub(),
                operand=dual_ast.Name(id='foo')
            )
        )

    def test_unary_Invert(self):
        self.template(
            ast.UnaryOp(
                op=ast.Invert(),
                operand=ast.Name(id='foo')
            ),
            dual_ast.UnaryOp(
                op=dual_ast.Invert(),
                operand=dual_ast.Name(id='foo')
            )
        )

    def test_unary_invalid_op(self):
        node = ast.UnaryOp(
            op='Blah',  # Not a valid operator
            operand=ast.Name(id="foo")
        )
        self.assertEqual(self.translator.visit(node), None)
        self.assertTrue(self.translator.errors)


class IfExpTestCase(NodeTestCase):
    """Tests for translation from IfExp"""
    def test_ifexp(self):
        self.template(
            ast.IfExp(
                test=ast.Name(id='bar'),
                body=ast.Name(id='foo'),
                orelse=ast.Name(id='baz')
            ),
            dual_ast.IfExp(
                test=dual_ast.Name(id='bar'),
                body=dual_ast.Name(id='foo'),
                orelse=dual_ast.Name(id='baz')
            )
        )


class ModuleTestCase(NodeTestCase):
    """Tests for translation from Module"""
    def test_empty_module(self):
        self.template(
            ast.Module([]),
            dual_ast.Module([])
        )

    def test_not_empty_module(self):
        self.template(
            ast.Module(
                body=[ast.Name(id='foo')]
            ),
            dual_ast.Module(
                body=[dual_ast.Name(id="foo")]
            )
        )

if __name__ == '__main__':
    unittest.main()
