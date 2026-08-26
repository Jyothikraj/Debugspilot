from tree_sitter import Language, Parser
import tree_sitter_java as tsjava


# --------------------------------------------------
# Java Language
# --------------------------------------------------

JAVA_LANGUAGE = Language(
    tsjava.language()
)

parser = Parser(JAVA_LANGUAGE)


# --------------------------------------------------
# Parse Java Code
# --------------------------------------------------

def parse_java_code(code):
    """
    Parse Java source code using Tree-sitter.
    """

    tree = parser.parse(
        code.encode("utf-8")
    )

    return tree


# --------------------------------------------------
# Get Node Text
# --------------------------------------------------

def get_node_text(node, source_code):
    """
    Get the exact source code represented
    by a Tree-sitter node.
    """

    return source_code[
        node.start_byte:node.end_byte
    ]


# --------------------------------------------------
# Extract Java Structure
# --------------------------------------------------

def extract_java_structure(
    tree,
    file_path,
    source_code
):

    functions = []
    classes = []
    imports = []
    packages = []
    calls = []
    variables = []
    exceptions = []
    interfaces = []
    enums = []

    root = tree.root_node


    # --------------------------------------------------
    # Recursive Traversal
    # --------------------------------------------------

    def walk(node, class_name=None):

        # ==================================================
        # IMPORT
        # ==================================================

        if node.type == "import_declaration":

            imports.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # PACKAGE
        # ==================================================

        elif node.type == "package_declaration":

            packages.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # CLASS
        # ==================================================

        elif node.type == "class_declaration":

            name_node = node.child_by_field_name(
                "name"
            )

            current_class = (
                get_node_text(
                    name_node,
                    source_code
                )
                if name_node
                else None
            )

            classes.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "file": str(file_path),
                "language": "java",
                "class": current_class,
                "function": None,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            })

            # Traverse class body
            for child in node.children:

                walk(
                    child,
                    current_class
                )

            return


        # ==================================================
        # INTERFACE
        # ==================================================

        elif node.type == "interface_declaration":

            name_node = node.child_by_field_name(
                "name"
            )

            interface_name = (
                get_node_text(
                    name_node,
                    source_code
                )
                if name_node
                else None
            )

            interfaces.append({
                "name": interface_name,
                "content": get_node_text(
                    node,
                    source_code
                ),
                "file": str(file_path),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            })


        # ==================================================
        # ENUM
        # ==================================================

        elif node.type == "enum_declaration":

            name_node = node.child_by_field_name(
                "name"
            )

            enum_name = (
                get_node_text(
                    name_node,
                    source_code
                )
                if name_node
                else None
            )

            enums.append({
                "name": enum_name,
                "content": get_node_text(
                    node,
                    source_code
                ),
                "file": str(file_path),
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            })


        # ==================================================
        # METHOD
        # ==================================================

        elif node.type == "method_declaration":

            name_node = node.child_by_field_name(
                "name"
            )

            function_name = (
                get_node_text(
                    name_node,
                    source_code
                )
                if name_node
                else None
            )

            functions.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "file": str(file_path),
                "language": "java",
                "class": class_name,
                "function": function_name,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            })


        # ==================================================
        # CONSTRUCTOR
        # ==================================================

        elif node.type == "constructor_declaration":

            name_node = node.child_by_field_name(
                "name"
            )

            constructor_name = (
                get_node_text(
                    name_node,
                    source_code
                )
                if name_node
                else None
            )

            functions.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "file": str(file_path),
                "language": "java",
                "class": class_name,
                "function": constructor_name,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
            })


        # ==================================================
        # METHOD CALL
        # ==================================================

        elif node.type == "method_invocation":

            name_node = node.child_by_field_name(
                "name"
            )

            if name_node:

                calls.append({
                    "name": get_node_text(
                        name_node,
                        source_code
                    ),
                    "line": node.start_point.row + 1
                })


        # ==================================================
        # OBJECT CREATION
        # ==================================================

        elif node.type == "object_creation_expression":

            type_node = node.child_by_field_name(
                "type"
            )

            if type_node:

                calls.append({
                    "name": get_node_text(
                        type_node,
                        source_code
                    ),
                    "type": "object_creation",
                    "line": node.start_point.row + 1
                })


        # ==================================================
        # LOCAL VARIABLES
        # ==================================================

        elif node.type == "local_variable_declaration":

            variables.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # FIELD DECLARATION
        # ==================================================

        elif node.type == "field_declaration":

            variables.append({
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # THROW
        # ==================================================

        elif node.type == "throw_statement":

            exceptions.append({
                "type": "throw",
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # CATCH
        # ==================================================

        elif node.type == "catch_clause":

            exceptions.append({
                "type": "catch",
                "content": get_node_text(
                    node,
                    source_code
                ),
                "line": node.start_point.row + 1
            })


        # ==================================================
        # Continue Traversal
        # ==================================================

        for child in node.children:

            walk(
                child,
                class_name
            )


    # Start AST traversal
    walk(root)


    # --------------------------------------------------
    # Return Structure
    # --------------------------------------------------

    return {
        "file": str(file_path),
        "language": "java",

        "functions": functions,
        "classes": classes,
        "imports": imports,
        "packages": packages,
        "calls": calls,
        "variables": variables,
        "exceptions": exceptions,
        "interfaces": interfaces,
        "enums": enums,
    }