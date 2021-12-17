import ast
import pyplant.models
import pyplant
import pyplant.parser
import importlib
import enum

import enum, ast


from pyplant.models import Package, Class, Attribute, Method

parsed_modules, packages = [], []

parsed_modules = []
packages = []


def parse_module(module_name):
    if module_name in parsed_modules:
        return

    print("Parsing module", module_name)

    current_module = importlib.import_module(module_name)
    parsed_modules.append(current_module.__name__)

    with open(current_module.__file__, "r") as file:
        node_tree = ast.parse(file.read())

    v = Visitor(current_module.__name__)
    v.visit(node_tree)

    packages.append(v.package)

    return packages

class Level(enum.IntEnum):
    PACKAGE = 1
    CLASS = 2
    METHOD = 3


class Visitor(ast.NodeVisitor):
    def __init__(self, package_name):
        self.indent = 0
        self.package = Package(package_name)
        self.obj_stack = [self.package]
        self.path_stack = [package_name]
        self.level = Level.PACKAGE

        self.attr_type = None

    def create_path(self, name: str = None):
        if name:
            return ".".join(self.path_stack + [str(name)])
        return ".".join(self.path_stack)

    def print(self, *args):
        print("  "*self.indent, end="")
        print(*args)

    def visit_Import(self, node):
        self.print("import: ", ", ".join([n.name for n in node.names]))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.print("from: ", str(node.module))
        self.print("-import: ", ", ".join([n.name for n in node.names]))
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.print("class: ", str(node.name))
        for base in node.bases:
            self.print("-base: ",base.value.id, "<-", base.attr)
        for keyword in node.keywords:
            self.print("-keyw: ", keyword)
        for deco in node.decorator_list:
            self.print("-deco: ", deco)
        #for stmt in node.body:
        #    self.print("-stmt: ", stmt)
        self.indent += 1
        last_level = self.level
        self.level = Level.CLASS

        self.obj_stack.append(Class(self.create_path(node.name)))
        self.obj_stack[-1].package = self.create_path()

        self.generic_visit(node)

        self.package.classes.append(self.obj_stack.pop(-1))
        self.level = last_level
        self.indent -= 1

    def visit_FunctionDef(self, node):
        self.print("func: ", str(node.name))
        if self.level == Level.CLASS:
            self.obj_stack[-1].methods.append(
                Method(self.create_path(node.name), None, None)
            )
        for stmt in node.body:
            self.print("-stmt: ", stmt)
        for expr in node.decorator_list:
            self.print("-expr: ", expr)
        self.indent += 1
        last_level = self.level
        if node.name != "__init__":
            self.level = Level.METHOD
        self.generic_visit(node)
        self.level = last_level
        self.indent -= 1

    def visit_Assign(self, node):
        self.print("assign: ")
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                continue
            if isinstance(target, ast.Name):
                self.print("-target: ", target.id)
                if self.level == Level.PACKAGE:
                    self.package.attributes.append(
                        Attribute(
                            self.create_path(target.id.lstrip("_")),
                            t=self.attr_type,
                            v=None
                        )
                    )
            else:
                self.print("-target: ", target)
        if isinstance(node.value, ast.Call):
            self.print(" -value:", node.value)
            if isinstance(node.value.func, ast.Name):
                self.print("   -func:", node.value.func.id)
            else:
                self.print("   -func:", node.value.func)
            for keyword in node.value.keywords:
                self.print("   -keyw;", keyword)
            for arg in node.value.args:
                if isinstance(arg, ast.Name):
                    self.print("   -arg;", arg.id)
                else:
                    self.print("   -arg;", arg)

        else:
            self.print(" -value:", node.value)
        if isinstance(node.value, ast.Str):
            self.attr_type = "string"
        elif isinstance(node.value, ast.Num):
            self.attr_type = type(node.value.n).__name__
        elif isinstance(node.value, ast.List):
            self.attr_type = "list"
        elif isinstance(node.value, ast.Tuple):
            self.attr_type = "tuple"
        elif isinstance(node.value, ast.Dict):
            self.attr_type = "dict"
        elif isinstance(node.value, ast.Set):
            self.attr_type = "set"

        self.indent += 1
        self.generic_visit(node)
        self.indent -= 1

    def visit_AugAssign(self, node):
        self.print("augAssign:", node.target)
        if isinstance(node.op, ast.Name):
            self.print(" -operation: ", node.op.id)
        else:
            self.print(" -opperation:", node.op)
        if isinstance(node.value, ast.Name):
            self.print(" -value: ", node.value.id)
            self.attr_type = node.value.id
        else:
            self.print(" -value:", node.value)
        self.indent += 1
        self.generic_visit(node)
        self.indent -= 1

    def visit_AnnAssign(self, node):
        self.print("annAssign:", node.target)
        if isinstance(node.annotation, ast.Name):
            self.print(" -annotation: ", node.annotation.id)
            self.attr_type = node.annotation.id
        else:
            self.print(" -annotation:", node.annotation)
        if isinstance(node.value, ast.Name):
            self.print(" -value: ", node.value.id)
        else:
            self.print(" -value:", node.value)
        self.print(" -simple:", node.simple)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            name = node.value.id + "." + node.attr.lstrip("_")
            self.print("attr: ", node.value.id, "<-", node.attr)
            if isinstance(node.value, ast.Name):
                self.print(" -attr:value: ", node.value.id)
            else:
                self.print(" -attr:value: ", node.value)
            if self.level == Level.CLASS and node.value.id == "self":
                if node.attr.startswith("__"):
                    visibility = "private"
                elif node.attr.startswith("_"):
                    visibility = "protected"
                else:
                    visibility = "public"
                self.obj_stack[-1].attributes.append(
                    Attribute(
                        self.create_path(name),
                        t=self.attr_type,
                        v=visibility
                    )
                )
                self.attr_type = None
        else:
            self.print("attr: ", node.value, "<-", node.attr)
        self.generic_visit(node)

class Base():
    pass

class Test():
    class_attr = 10
    def __init__(self, parameter):
        self.parameter = parameter
        self.array = []
        self.string:str = "string"
        self.integer:int = 42
        self.integer += 42
        self.float:float = 42
        self._protected = "protected"
        self.__private = "private"

        Test.class_attr = Test.class_attr + 1

        self.first, self.second = (0, 1)

        self.first = self.second = 1

        self.b_in_func = isinstance

        #local_attr = "this is not an object arrt"

    #class InnerClass(Base):
    #    class InnerInnerClass(Package):
    #        pass
    #    pass

