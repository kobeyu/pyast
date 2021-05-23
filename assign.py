import ast
import astunparse

code = """
a = 0
"""



root = ast.parse(code)


for n in ast.walk(root):
    print(n)


#add code to the end of script
root.body.append(ast.Assign(targets=[ast.Name(id="_watchpoints_localvar", ctx=ast.Store())],value=ast.Constant(value=38)))

#add code to the head of script
gv = ast.Assign(targets=[ast.Name(id='RETURN', ctx=ast.Store())], value = ast.Constant(5))
root.body.insert(0, gv)


#issue... https://github.com/simonpercivall/astunparse/issues/43
ast.fix_missing_locations(root)




print(astunparse.unparse(root))
exec(compile(root, filename="rm_print_code", mode="exec"))
