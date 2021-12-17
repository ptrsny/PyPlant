class Base():
    def __init__(self, path: str):
        self.__indent = 0
        self.path = path
        self.name = path.split(".")[-1]

    def __repr__(self):
        return self.path


class Package(Base):
    def __init__(self, path):
        super().__init__(path)
        self.packages = []
        self.imports = []
        self.classes = []
        self.attributes = []
        self.functions = []

    def __str__(self):
        s = super().__str__()
        s += "\n Imports: "
        if self.imports:
            s += "\n  -" + "\n  -".join([str(imp) for imp in self.imports])
        s += "\n Classes: "
        if self.classes:
            s += "\n  -" + "\n  -".join([str(clz) for clz in self.classes])
        s += "\n Attributes: "
        if self.attributes:
            s += "\n  -" + "\n  -".join([str(attr) for attr in self.attributes])
        s += "\n Functions: "
        if self.functions:
            s += "\n  -" + "\n  -".join([str(func) for func in self.functions])
        return s


class Class(Base):
    def __init__(self, path):
        super().__init__(path)
        self.bases = []
        self.package = None
        self.attributes = []
        self.methods = []

    def __str__(self):
        s = super().__str__()
        s += "\n Attributes: "
        if self.attributes:
            s += "\n  -" + "\n  -".join([str(attr) for attr in self.attributes])
        s += "\n methods: "
        if self.methods:
            s += "\n  -" + "\n  -".join([str(meth) for meth in self.methods])
        return s


class Attribute(Base):
    def __init__(self, path, t, v):
        super().__init__(path)
        self.type = t
        self.viewability = v
        self.parameters = []


class Method(Base):
    def __init__(self, path, v, rt=None):
        super().__init__(path)
        self.viewability = v
        self.return_type = rt
        self.parameters = []


class Parameter(Base):
    def __init__(self, path, t):
        super().__init__(path)
        self.type = t

