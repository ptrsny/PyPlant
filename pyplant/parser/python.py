from pyplant.models import Package, Class, Attribute, Method

import importlib
import inspect


parsed_modules = []

internal_attributes = [
    "__all__",
    "__author__",
    "__builtins__",
    "__cached__",
    "__credits__",
    "__doc__",
    "__file__",
    "__loader__",
    "__name__",
    "__package__",
    "__path__",
    "__build_class__",
    "__debug__",
    "__import__",
    "__version__",
    "__spec__",
]


def parse_path(path: str):
    spec = importlib.util.spec_from_file_location("module", path)
    module = importlib.util.module_from_spec(spec)

    module = spec.loader.exec_module(module)

    return parse_module(module)

def bananaphone():
    pass

def parse_module(module: str, packages: list=[], parent_package: Package=None):
    if module in parsed_modules:
        return
    print("Parsing module", module)
    current_module = importlib.import_module(module)
    parsed_modules.append(current_module.__name__)
    package = Package(current_module.__name__)

    def isattribute(member):
        return not inspect.ismodule(member) and \
               not inspect.ismethod(member) and \
               not inspect.isfunction(member) and \
               not inspect.isclass(member) and \
               not callable(member)

    for module_name, module in inspect.getmembers(current_module, inspect.ismodule):
        parse_module(module.__name__, packages, package)

    for clazz_name, clazz in inspect.getmembers(current_module, inspect.isclass):
        clz = Class(clazz.__name__)
        clz.package = clazz.__module__

        inherited_attributes = []
        inherited_methods = []

        for base in clazz.__bases__:
            clz.bases.append(base.__name__)
            inherited_attributes += map(
                    lambda x: x[0],
                    inspect.getmembers(base)
            )
            inherited_methods += map(
                    lambda x: x[0],
                    inspect.getmembers(base)
            )

        # Parse attributes of class
        for attr_name, attr_value in inspect.getmembers(current_module, isattribute):
            if attr_name in internal_attributes:
                continue
            if attr_name in inherited_attributes:
                continue
            if attr_name.startswith("__"):
                attr = Attribute(
                        attr_name,
                        t=type(attr_value).__name__,
                        v="private")
            elif attr_name.startswith("_"):
                attr = Attribute(
                        attr_name,
                        t=type(attr_value).__name__,
                        v="protected")
            else:
                attr = Attribute(
                        attr_name,
                        t=type(attr_value).__name__,
                        v="public")
            clz.attributes.append(attr)

        # Parse methods of class
        for meth_name, meth in inspect.getmembers(current_module, inspect.ismethod):
            if meth_name in inherited_methods:
                continue
            if meth_name.startswith("__"):
                meth = Method(
                        meth_name,
                        rt=inspect.signature(meth).return_annotation.__name__,
                        v="private")
            elif meth_name.startswith("_"):
                meth = Method(
                        meth_name,
                        rt=inspect.signature(meth).return_annotation.__name__,
                        v="protected")
            else:
                meth = Method(
                        meth_name,
                        rt=inspect.signature(meth).return_annotation.__name__,
                        v="public")
            clz.methods.append(meth)
        package.classes.append(clz)

    # Parse attributes of module
    for attr_name, attr_value in inspect.getmembers(current_module, isattribute):
        if attr_name in internal_attributes:
            continue
        if attr_name.startswith("__"):
            attr = Attribute(
                    attr_name,
                    t=type(attr_value).__name__,
                    v="private")
        elif attr_name.startswith("_"):
            attr = Attribute(
                    attr_name,
                    t=type(attr_value).__name__,
                    v="protected")
        else:
            attr = Attribute(
                    attr_name,
                    t=type(attr_value).__name__,
                    v="public")
        package.attributes.append(attr)

    # Parse function of module
    for func_name, func in inspect.getmembers(current_module, inspect.isfunction):
        if func_name.startswith("__"):
            func = Method(
                    func_name,
                    rt=inspect.signature(func).return_annotation.__name__,
                    v="private")
        elif func_name.startswith("_"):
            func = Method(
                    func_name,
                    rt=inspect.signature(func).return_annotation.__name__,
                    v="protected")
        else:
            func = Method(
                    func_name,
                    rt=inspect.signature(func).return_annotation.__name__,
                    v="public")
        package.functions.append(func)

    if parent_package and current_module.__name__.startswith(parent_package.name):
        print(f"Add package {package.name} to {parent_package.name} as subpackage")
        parent_package.packages.append(package)
    else:
        packages.append(package)
        print(f"parent_package is None -> {package.name}")

    return packages

