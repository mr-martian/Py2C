#A node visitor that spews C++ when told to visit a node
#This include every node defined in /py2c/syntax_tree/python.py
import ast
from syntax_tree import python
from textwrap import indent

class tocpp(ast.NodeVistor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.imports = set('__builtins__') #all files imported
        self.context = [] #append current node before entering children unless they definitely don't need it
    def visit_PyAST(self, node): return self.generic_visit(node)
    def visit_mod(self, node): return self.generic_visit(node)
    def visit_stmt(self, node): return self.generic_visit(node)
    def visit_expr(self, node): return self.generic_visit(node)
    def visit_expr_context(self, node): return self.generic_visit(node)
    def visit_slice(self, node): return self.generic_visit(node)
    def visit_boolop(self, node): return self.generic_visit(node)
    def visit_operator(self, node): return self.generic_visit(node)
    def visit_unaryop(self, node): return self.generic_visit(node)
    def visit_cmpop(self, node): return self.generic_visit(node)
    def visit_arg(self, node): return self.generic_visit(node)
    def visit_comprehension(self, node): return self.generic_visit(node)
    def visit_arguments(self, node): return self.generic_visit(node)
    def visit_keyword(self, node): return self.generic_visit(node)
    def visit_alias(self, node): return self.generic_visit(node)
    def visit_withitem(self, node): return self.generic_visit(node)
    def visit_ExceptHandler(self, node): return self.generic_visit(node)
    def visit_Module(self, node):
        strings = list(self.visit(n) for n in node.body)
        imports = list('#include "%s"' % n for n in list(self.imports))
        return '\n'.join(imports) + '\n' + '\n'.join(strings)
    def visit_FunctionDef(self, node): return self.generic_visit(node)
    def visit_ClassDef(self, node): return self.generic_visit(node)
    def visit_Return(self, node): return self.generic_visit(node)
    def visit_Delete(self, node): return self.generic_visit(node)
    def visit_Assign(self, node): return self.generic_visit(node)
    def visit_AugAssign(self, node): return self.generic_visit(node)
    def visit_For(self, node): return self.generic_visit(node)
    def visit_While(self, node): return self.generic_visit(node)
    def visit_If(self, node):
        ts = self.visit(node.test)
        yes = indent('    ', '\n'.join(list(self.visit(n) for n in node.body)))
        no = list(self.visit(n) for n in node.orelse)
        if no:
            n = indent('    ', '\n'.join(no))
            return 'if (%s) {\n%s\n}\nelse {\n%s\n}\n' % (ts, yes, n)
        else:
            return 'if (%s) {\n%s\n}\n' % (ts, yes)
    def visit_With(self, node): return self.generic_visit(node)
    def visit_Raise(self, node): return self.generic_visit(node)
    def visit_Try(self, node): return self.generic_visit(node)
    def visit_Assert(self, node): return self.generic_visit(node)
    def visit_Import(self, node): return self.generic_visit(node)
    def visit_ImportFrom(self, node): return self.generic_visit(node)
    def visit_Future(self, node): return self.generic_visit(node)
    def visit_Global(self, node): return self.generic_visit(node)
    def visit_Nonlocal(self, node): return self.generic_visit(node)
    def visit_Expr(self, node): return self.generic_visit(node)
    def visit_Pass(self, node): return self.generic_visit(node)
    def visit_Break(self, node): return self.generic_visit(node)
    def visit_Continue(self, node): return self.generic_visit(node)
    def visit_BoolOp(self, node): return self.generic_visit(node)
    def visit_BinOp(self, node):
        l = self.visit(node.left)
        r = self.visit(node.right)
        if node.op.__class__ == python.FloorDiv:
            return '(%s - (%s %% %s)) / %s' % (l, l, r, r)
        else:
            return '%s %s %s' % (l, self.visit(node.op), r)
    def visit_UnaryOp(self, node): return self.generic_visit(node)
    def visit_Lambda(self, node): return self.generic_visit(node)
    def visit_IfExp(self, node): return self.generic_visit(node)
    def visit_Dict(self, node): return self.generic_visit(node)
    def visit_Set(self, node): return self.generic_visit(node)
    def visit_ListComp(self, node): return self.generic_visit(node)
    def visit_SetComp(self, node): return self.generic_visit(node)
    def visit_DictComp(self, node): return self.generic_visit(node)
    def visit_GeneratorExp(self, node): return self.generic_visit(node)
    def visit_Yield(self, node): return self.generic_visit(node)
    def visit_YieldFrom(self, node): return self.generic_visit(node)
    def visit_Compare(self, node): return self.generic_visit(node)
    def visit_Call(self, node): return self.generic_visit(node)
    def visit_Attribute(self, node): return self.generic_visit(node)
    def visit_Subscript(self, node): return self.generic_visit(node)
    def visit_Starred(self, node): return self.generic_visit(node)
    def visit_Name(self, node): return self.generic_visit(node)
    def visit_List(self, node): return self.generic_visit(node)
    def visit_Tuple(self, node): return self.generic_visit(node)
    def visit_Ellipsis(self, node): return self.generic_visit(node)
    def visit_NameConstant(self, node): return self.generic_visit(node)
    def visit_literal(self, node): return self.generic_visit(node)
    def visit_Str(self, node): return self.generic_visit(node)
    def visit_Bytes(self, node): return self.generic_visit(node)
    def visit_Bool(self, node): return self.generic_visit(node)
    def visit_num(self, node): return self.generic_visit(node)
    def visit_Int(self, node):
        return str(node.n)
    def visit_Float(self, node): return self.generic_visit(node)
    def visit_Complex(self, node): return self.generic_visit(node)
    def visit_Load(self, node): return self.generic_visit(node)
    def visit_Store(self, node): return self.generic_visit(node)
    def visit_Del(self, node): return self.generic_visit(node)
    def visit_AugLoad(self, node): return self.generic_visit(node)
    def visit_AugStore(self, node): return self.generic_visit(node)
    def visit_Param(self, node): return self.generic_visit(node)
    def visit_Slice(self, node): return self.generic_visit(node)
    def visit_ExtSlice(self, node): return self.generic_visit(node)
    def visit_Index(self, node): return self.generic_visit(node)
    def visit_And(self, node):
        return 'and'
    def visit_Or(self, node):
        return 'or'
    def visit_Add(self, node):
        return '+'
    def visit_Sub(self, node):
        return '-'
    def visit_Mult(self, node):
        return '*'
    def visit_Div(self, node):
        return '/'
    def visit_Mod(self, node): return self.generic_visit(node)
    def visit_Pow(self, node): return self.generic_visit(node)
    def visit_LShift(self, node):
        return '<<'
    def visit_RShift(self, node):
        return '>>'
    def visit_BitOr(self, node):
        return '|'
    def visit_BitXor(self, node):
        return '^'
    def visit_BitAnd(self, node):
        return '&'
    def visit_FloorDiv(self, node): return self.generic_visit(node)
    def visit_Invert(self, node):
        return '~'
    def visit_Not(self, node):
        return '!'
    def visit_UAdd(self, node):
        return '+'
    def visit_USub(self, node):
        return '-'
    def visit_Eq(self, node):
        return '=='
    def visit_NotEq(self, node):
        return '!='
    def visit_Lt(self, node):
        return '<'
    def visit_LtE(self, node):
        return '<='
    def visit_Gt(self, node):
        return '>'
    def visit_GtE(self, node):
        return '>='
    def visit_Is(self, node): return self.generic_visit(node)
    def visit_IsNot(self, node): return self.generic_visit(node)
    def visit_In(self, node): return self.generic_visit(node)
    def visit_NotIn(self, node): return self.generic_visit(node)
    