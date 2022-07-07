from io import TextIOWrapper
from itertools import groupby
from os.path import exists, join
import ast
import builtins
import sys


class Transformer(ast.NodeTransformer):

    def __init__(self):
        self.name_list = []
        self.parent = None

    def visit(self, node):
        node.parent = self.parent
        self.parent = node
        node = super().visit(node)
        if hasattr(node, 'name') and len(node.name) == 1:
            raise AssertionError(f'Error in line {node.lineno}: {node.name} node names cannot be single letter.')
        if hasattr(node, 'id') and len(node.id) == 1 and (node.id != '_'):
            raise AssertionError(f'Error in line {node.lineno}: {node.id} node names cannot be single letter.')
        if isinstance(node, ast.AST):
            self.parent = node.parent
        return node

    def visit_Assign(self, node):
        super().generic_visit(node)
        if isinstance(node.value, ast.Lambda):
            raise AssertionError(f'Error in line {node.lineno}: Lambda assignments are forbidden.')
        for node_target in node.targets:
            if hasattr(node_target, 'id') and node_target.id in dir(builtins):
                raise AssertionError(f'Error in line {node.lineno}: {node_target.id} assignments to builtin names are forbidden.')
        return node

    def visit_Call(self, node):
        super().generic_visit(node)
        if hasattr(node.func, 'attr') and node.func.attr == 'format' and isinstance(node.func.value, ast.Constant):
            raise AssertionError(f'Error in line {node.lineno}: printf strings are forbidden.')
        if hasattr(node.func, 'id') and node.func.id in ['breakpoint', 'print']:
            return None
        else:
            return node

    def visit_ClassDef(self, node):
        super().generic_visit(node)
        if not node.name[0].isupper():
            raise AssertionError(f'Error in line {node.lineno}: Class names should be capitalized.')
        for node_in_body in node.body:
            if not isinstance(node_in_body, ast.FunctionDef):
                raise AssertionError(f'Error in line {node_in_body.lineno}: Classes can only contain defs.')
        if not isinstance(node.parent, ast.Module):
            raise AssertionError(f'Error in line {node.lineno}: Classes can only reside in the module.')
        base_class_list = []
        for node_base in node.bases:
            if not (hasattr(node_base, 'id') and node_base.id == 'object'):
                base_class_list.append(node_base)
        node.bases = base_class_list
        def_in_class_list = []
        for node_in_body in node.body:
            def_in_class_list.append(node_in_body)
        def_in_class_list.sort(key=lambda def_in_class: def_in_class.name)
        node.body = def_in_class_list
        return node

    def visit_Compare(self, node):
        super().generic_visit(node)
        if isinstance(node.ops[0], ast.Eq) and isinstance(node.left, ast.Call) and hasattr(node.left.func, 'id') and (node.left.func.id == 'type'):
            new_node = ast.Call(ast.Name('isinstance'), args=[node.left.args, node.comparators], keywords=[])
            new_node.parent = node.parent
            return new_node
        for (index, (ops, comparators)) in enumerate(zip(node.ops, node.comparators)):
            if isinstance(comparators, ast.Constant):
                if str(comparators.s) in ['None', 'True', 'False']:
                    if isinstance(ops, ast.Eq):
                        node.ops[index] = ast.Is()
                    elif isinstance(ops, ast.NotEq):
                        node.ops[index] = ast.IsNot()
                elif isinstance(ops, ast.Is):
                    node.ops[index] = ast.Eq()
                elif isinstance(ops, ast.IsNot):
                    node.ops[index] = ast.NotEq()
        return node

    def visit_Expr(self, node):
        super().generic_visit(node)
        if hasattr(node, 'value') and isinstance(node.value, ast.Call):
            return node
        else:
            return None

    def visit_For(self, node):
        super().generic_visit(node)
        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            return None
        else:
            return node

    def visit_FunctionDef(self, node):
        super().generic_visit(node)
        if len(node.args.args) > 1:
            arg_list = [element.arg for element in node.args.args]
            if 'self' in arg_list:
                arg_list.remove('self')
            if arg_list != sorted(arg_list):
                raise AssertionError(f'Error in line {node.lineno}: {node.name} unsorted def arguments are forbidden.')
        node.returns = None
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        if not isinstance(node.parent, (ast.Module, ast.ClassDef)):
            raise AssertionError(f'Error in line {node.lineno}: Functions outside Modules or Classes are forbidden.')
        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            raise AssertionError(f'Error in line {node.lineno}: {node.name} empty def is forbidden.')
        return node

    def visit_Global(self, node):
        super().generic_visit(node)
        raise AssertionError(f'Error in line {node.lineno}: Globals are forbidden.')

    def visit_If(self, node):
        super().generic_visit(node)
        if isinstance(node.test, ast.UnaryOp) and isinstance(node.test.op, ast.Not) and hasattr(node.test.operand, 'ops'):
            if isinstance(node.test.operand.ops[0], ast.In):
                new_operator = ast.NotIn()
            elif isinstance(node.test.operand.ops[0], ast.Is):
                new_operator = ast.IsNot()
            new_node = ast.If(test=ast.Compare(left=node.test.operand.left, ops=[new_operator], comparators=node.test.operand.comparators), body=node.body, orelse=node.orelse)
            new_node.parent = node.parent
            return new_node
        if not node.body or (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)):
            return None
        else:
            return node

    def visit_Import(self, node):
        super().generic_visit(node)
        module_filename = join(sys.path[0], f'{node.names[0].name}.py')
        for node_name in node.names:
            if '.' in node_name.name:
                raise AssertionError(f'Error in line {node_name.lineno}: Imports submodules is forbidden.')
        if not isinstance(node.parent, ast.Module):
            raise AssertionError(f'Error in line {node.lineno}: Imports can only reside in the module.')
        if exists(module_filename):
            raise AssertionError(f'Error in line {node.lineno}: Importing from local modules is forbidden.')
        node_name_list = [node_name.name for node_name in node.names]
        if 'logging' in node_name_list:
            raise AssertionError(f'Error in line {node.lineno}: Importing logging is forbidden.')
        elif 'argparse' in node_name_list:
            raise AssertionError(f'Error in line {node.lineno}: Importing argparse is forbidden.')
        return node

    def visit_ImportFrom(self, node):
        super().generic_visit(node)
        module_filename = join(sys.path[0], f'{node.module}.py')
        if not isinstance(node.parent, ast.Module):
            raise AssertionError(f'Error in line {node.lineno}: Import Froms can only reside in the module.')
        if exists(module_filename):
            raise AssertionError(f'Error in line {node.lineno}: Importing from local modules is forbidden.')
        if node.module in ['argparse', 'logging']:
            raise AssertionError(f'Error in line {node.lineno}: Importing {node.module} is forbidden.')
        if node.names[0].name == '*':
            raise AssertionError(f'Error in line {node.lineno}: Importing from * is forbidden.')
        if node.level > 0:
            raise AssertionError(f'Error in line {node.lineno}: Relative imports are forbidden.')
        return node

    def visit_Module(self, node):
        super().generic_visit(node)
        for node_in_body in node.body:
            if not isinstance(node_in_body, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef)):
                if not (isinstance(node_in_body, ast.If) and hasattr(node_in_body, 'test') and (node_in_body.test.left.id == '__name__')):
                    raise AssertionError(f'Error in line {node_in_body.lineno}: Child modules should be only imports, classes, defs, or if __name__.')
        return node

    def visit_Name(self, node):
        super().generic_visit(node)
        if isinstance(node.parent, ast.Assign):
            if node.id != '_' and (not node.id.islower()):
                raise AssertionError(f'Error in line {node.lineno}: Assignment names should be lowercased.')
        self.name_list.append(node.id)
        return node

    def visit_Try(self, node):
        raise AssertionError(f'Error in line {node.lineno}: Try except is forbidden.')


def main():
    if len(sys.argv) == 2:
        output = source_code_normalizer(sys.argv[1])
        sys.stdout.write(output)


def source_code_normalizer(code_input):
    if isinstance(code_input, str):
        with open(code_input) as file:
            root = ast.parse(file.read())
    elif isinstance(code_input, TextIOWrapper):
        root = ast.parse(code_input.read())
    transformer = Transformer()
    ast.fix_missing_locations(transformer.visit(root))
    class_list = []
    def_list = []
    import_from_list = []
    import_list = []
    import_name_list = []
    rest_list = []
    for node_in_body in root.body:
        if isinstance(node_in_body, ast.Import):
            for node_name in node_in_body.names:
                if node_name.asname:
                    node_name_name = node_name.asname
                else:
                    node_name_name = node_name.name
                if node_name_name not in import_name_list and node_name_name in transformer.name_list:
                    import_name_list.append(node_name.name)
                    if node_name.asname:
                        new_node = ast.Import(names=[ast.alias(node_name.name, asname=node_name.asname)])
                    else:
                        new_node = ast.Import(names=[ast.alias(node_name.name)])
                    import_list.append(new_node)
        elif isinstance(node_in_body, ast.ImportFrom):
            import_from_list.append(node_in_body)
        elif isinstance(node_in_body, ast.ClassDef):
            class_list.append(node_in_body)
        elif isinstance(node_in_body, ast.FunctionDef):
            def_list.append(node_in_body)
        else:
            rest_list.append(node_in_body)
    import_from_group_list_list = [list(grouped) for (_, grouped) in groupby(import_from_list, lambda element: element.module)]
    import_from_list = []
    for import_from_group_list in import_from_group_list_list:
        import_from_name_list = []
        for import_from_group in import_from_group_list:
            for import_from_group_name in import_from_group.names:
                import_from_name_name_list = [import_from_name.name for import_from_name in import_from_name_list]
                if import_from_group_name.asname:
                    import_from_group_name_name = import_from_group_name.asname
                else:
                    import_from_group_name_name = import_from_group_name.name
                if import_from_group_name.name not in import_from_name_name_list and import_from_group_name_name in transformer.name_list:
                    import_from_name_list.append(import_from_group_name)
        import_from_name_list.sort(key=lambda element: element.name)
        if import_from_name_list:
            new_node = ast.ImportFrom(module=import_from_group.module, names=import_from_name_list, level=import_from_group.level)
            import_from_list.append(new_node)
    class_list.sort(key=lambda element: element.name)
    def_list.sort(key=lambda element: element.name)
    import_from_list.sort(key=lambda element: element.module)
    import_list.sort(key=lambda element: element.names[0].name)
    root.body = import_from_list + import_list + class_list + def_list + rest_list
    root = ast.parse(ast.unparse(root))
    transformer = Transformer()
    ast.fix_missing_locations(transformer.visit(root))
    output = ast.unparse(root)
    line_list = output.split('\n')
    if '' in line_list:
        line_list = list(filter(lambda element: element != '', line_list))
    name_main_index = line_list.index("if __name__ == '__main__':")
    line_list.insert(name_main_index, '')
    line_list.insert(name_main_index, '')
    def_indices = [index for (index, element) in enumerate(line_list) if element.startswith('def ')]
    for def_index in reversed(def_indices):
        if def_index > 0:
            line_list.insert(def_index, '')
            line_list.insert(def_index, '')
    class_def_indices = [index for (index, element) in enumerate(line_list) if element.startswith('    def ')]
    for def_index in reversed(class_def_indices):
        if def_index > 0:
            if line_list[def_index - 1].startswith('    @'):
                line_list.insert(def_index - 1, '')
            else:
                line_list.insert(def_index, '')
    class_indices = [index for (index, element) in enumerate(line_list) if element.startswith('class ')]
    for def_index in reversed(class_indices):
        if def_index > 0:
            line_list.insert(def_index, '')
            line_list.insert(def_index, '')
    output = '\n'.join(line_list)
    output += '\n'
    return output


if __name__ == '__main__':
    main()
