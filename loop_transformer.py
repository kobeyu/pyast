import ast
import sys
import astunparse



code = """

for idx in range(10):
    gg = idx
"""


def print_ast(root):
    for n in ast.walk(root):
        print(n.lineno)






# ref: https://stackoverflow.com/questions/51148730/how-to-instrument-python-ast-for-tracing-store-operations
class ForLoopRewriter(ast.NodeTransformer):
    def __init__(self, nodes_to_insert):
        super().__init__()
        self.nodes_to_insert = nodes_to_insert

    def visit_For(self, node):
        # redirect the assignment to a usually invalid variable name so it
        # doesn't clash with other variables in the code
        target = ast.Name('_loop_var', ast.Store())

        # insert the new nodes
        loop_body = self.nodes_to_insert.copy()

        # then reassign the loop variable to the actual target
        reassign = ast.Assign([node.target], ast.Name('_loop_var', ast.Load()))
        loop_body.append(reassign)

        # visit all the ast nodes in the loop body
        for n in node.body:
            loop_body.append(self.visit(n))

        # make a new For node and return it
        new_node = ast.For(target, node.iter, loop_body, node.orelse)
        ast.fix_missing_locations(new_node)
        return new_node



root = ast.parse(code)
root.body.insert(0, ast.Assign(targets=[ast.Name(id="_loop_var", ctx=ast.Store())],value=ast.Constant(value=0)))
ast.fix_missing_locations(root)

tc = ast.parse('print("code to trace")').body
#root.body.append(tc)



#gv = ast.Assign(targets=[ast.Name(id='RETURN', ctx=ast.Store())], value = ast.Constant(5))
#imp = ast.Import(names=[ast.alias(name='onnx', asname=None)], col_offset = 8)



ForLoopRewriter(tc).visit(root)
ast.fix_missing_locations(root)

pc = ast.parse('print(_loop_var)').body
root.body.append(pc)
ast.fix_missing_locations(root)

print_ast(root)
print(astunparse.unparse(root))
exec(compile(root, filename="rm_print_code", mode="exec"))


