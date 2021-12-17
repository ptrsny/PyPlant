from pyplant.models import Package, Class, Attribute, Method

file = open("class-diagramm.puml", "w+")


def write_class(clazz):
    print(f"Plotting class {clazz.path}")
    extends = ""
    if clazz.bases:
        extends = f"<? extends {', '.join(clazz.bases)}>"
    file.write(f"class {clazz.name}{extends}" + " {\n")
    for attr in clazz.attributes:
        file.write("{field}" + f"{attr.name} : {attr.type}\n")
    for meth in clazz.methods:
        file.write("{method}" + f"{meth.name}(TBD) : {meth.return_type}\n")
    file.write("}\n\n")


def write_package(package: Package, parent_package: Package=None):
    print(f"Plotting package {package.path} with {len(package.packages)} subpackages")
    file.write(f"package {package.name}" + " {\n")
    for pack in package.packages:
        write_package(pack, package)
    for clazz in package.classes:
        if clazz.package and clazz.package.startswith(package.path):
            write_class(clazz)
    file.write("}\n\n")


def plant(packages):
    file.write("@startuml\n\n")

    for package in packages:
        write_package(package)

    file.write("@enduml\n")

    file.close()
