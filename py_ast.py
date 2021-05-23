import ast
import sys
import astunparse

code = """
a = [1, 2, 3, 4]
b = [5, 6, 7, 8]
sum = []
for i in range(len(a)):
    sum.append(a[i] + b[i])
print(sum)
"""

code1 = """
a = 1
for idx in range(10):
    a = 1
    print(idx)
"""

code2 = """
a = 1
"""

root = ast.parse(code2)

import_node = ast.Import(names=[ast.alias(name='quux', asname=None)])
#col_offset=node_span.col_offset
print(root.body)
a = ast.Assign([ast.Name('aabb', ast.Store())], ast.Constant(1))
for n in ast.walk(root):
    print(n)
    if isinstance(n, ast.Assign):
        print("Assign:", n.targets[0].id)

        v = n.value
        if isinstance(v, ast.Str):
            print("this value of assign is str")
            print(v.s)
        elif isinstance(v, ast.Num):
            print("this value of assign is num")
            print(v.n)
        continue
        #print(n.targets[0].value)
        #ast.Assign([ast.Name(name, ast.Store())], form)
        
        #aa = ast.Assign(targets=[ast.Name(id='RETURN', ctx=ast.Store())], value=ast.Constant(2), lineno=n.lineno),
        #root.body.insert(n.lineno+1, aa)
    elif isinstance(n, ast.Name):
        print("Name:", n.id)
    elif isinstance(n, ast.For):
        print("got for!")
        in2 = ast.Import(names=[ast.alias(name='onnx', asname=None)], col_offset = 8)
        aa = ast.Assign(targets=[ast.Name(id='RETURN', ctx=ast.Store())], value=ast.Constant(2), lineno=n.lineno),
        #ast.copy_location(in2, n)
        #root.body.insert(n.lineno-1, aa)
        print(n.target.id)
        print(n.body[0].col_offset)
        #print(n.body[0].end_col_offset)

print(astunparse.unparse(root))


