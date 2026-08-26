from tree_sitter import Language, Parser
import tree_sitter_cpp as tscpp


# ============================================================
# C++ LANGUAGE
# ============================================================

CPP_LANGUAGE = Language(
    tscpp.language()
)

parser = Parser(
    CPP_LANGUAGE
)


# ============================================================
# PARSE C++ CODE
# ============================================================

def parse_cpp_code(code):
    """
    Parse C++ source code using Tree-sitter.
    """

    return parser.parse(
        code.encode("utf-8")
    )


# ============================================================
# GET NODE TEXT
# ============================================================

def get_node_text(
    node,
    source_code
):
    """
    Return the exact source code represented
    by a Tree-sitter node.
    """

    return source_code[
        node.start_byte:node.end_byte
    ]


# ============================================================
# EXTRACT C++ STRUCTURE
# ============================================================

def extract_cpp_structure(
    tree,
    file_path,
    source_code
):
    """
    Extract only C++ classes and functions.

    No complicated metadata extraction.

    Function bodies are never traversed.

    Output:
        functions
        classes
    """

    functions = []
    classes = []

    root = tree.root_node


    # ========================================================
    # AST WALK
    # ========================================================

    def walk(
        node,
        current_class=""
    ):

        # ----------------------------------------------------
        # FUNCTION
        # ----------------------------------------------------

        if node.type == "function_definition":

            functions.append({

                "type": "function",

                "file": str(
                    file_path
                ),

                "language": "cpp",

                "class": current_class,

                "function": "",

                "content": get_node_text(
                    node,
                    source_code
                ),

                "start_line":
                    node.start_point.row + 1,

                "end_line":
                    node.end_point.row + 1,
            })

            # IMPORTANT
            #
            # Do not traverse inside the function.
            #
            # This prevents walking through every
            # statement/expression in the function body.

            return


        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        if node.type == "class_specifier":

            name_node = node.child_by_field_name(
                "name"
            )

            class_name = ""

            if name_node is not None:

                class_name = get_node_text(
                    name_node,
                    source_code
                )

            classes.append({

                "type": "class",

                "file": str(
                    file_path
                ),

                "language": "cpp",

                "class": class_name,

                "function": "",

                "content": get_node_text(
                    node,
                    source_code
                ),

                "start_line":
                    node.start_point.row + 1,

                "end_line":
                    node.end_point.row + 1,
            })


            # ------------------------------------------------
            # Traverse class children.
            #
            # If a function_definition is encountered,
            # walk() returns immediately and does not enter
            # the function body.
            # ------------------------------------------------

            for child in node.children:

                walk(
                    child,
                    class_name
                )

            return


        # ----------------------------------------------------
        # OTHER STRUCTURAL NODES
        # ----------------------------------------------------

        for child in node.children:

            walk(
                child,
                current_class
            )


    # ========================================================
    # START AST WALK
    # ========================================================

    walk(
        root
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "file": str(
            file_path
        ),

        "language": "cpp",

        "functions": functions,

        "classes": classes,
    }