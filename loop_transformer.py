import ast
import sys
import astunparse

code = """
for idx in range(10):
    i  = idx
"""

def print_ast(root):
    for n in ast.walk(root):
#        print(n)
        if isinstance(n, ast.For):
            root.body.insert(n.lineno - 1, ast.Assign(targets=[ast.Name(id="_loop_var0", ctx=ast.Store())],value=ast.Constant(value=0)))
            root.body.insert(n.lineno+1,ast.Call(ast.Name('\nprint', ast.Load()), [ast.Name('_loop_var0', ast.Load())], []))
            ast.fix_missing_locations(root)
        if isinstance(n, ast.Expr) or isinstance(n, ast.stmt):
            pass


# ref: https://stackoverflow.com/questions/51148730/how-to-instrument-python-ast-for-tracing-store-operations
class ForLoopRewriter(ast.NodeTransformer):
    def __init__(self, nodes_to_insert):
        super().__init__()
        self.nodes_to_insert = nodes_to_insert

    def visit_For(self, node):
        # redirect the assignment to a usually invalid variable name so it
        # doesn't clash with other variables in the code
        target = ast.Name('_loop_var0', ast.Store())

        # insert the new nodes
        loop_body = self.nodes_to_insert.copy()

        # then reassign the loop variable to the actual target
        reassign = ast.Assign([node.target], ast.Name('_loop_var0', ast.Load()))
        loop_body.append(reassign)

        # visit all the ast nodes in the loop body
        for n in node.body:
            loop_body.append(self.visit(n))

        # make a new For node and return it
        new_node = ast.For(target, node.iter, loop_body, node.orelse)
        ast.fix_missing_locations(new_node)
        return new_node



root = ast.parse(code)

tc = ast.parse('print("code to trace")').body
ForLoopRewriter(tc).visit(root)


print_ast(root)
ast.fix_missing_locations(root)

print(astunparse.unparse(root))
#exec(compile(root, filename="rm_print_code", mode="exec"))


