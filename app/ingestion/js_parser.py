from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjavascript


# ============================================================
# JavaScript Language
# ============================================================

JS_LANGUAGE = Language(
    tsjavascript.language()
)


# ============================================================
# Parse JavaScript
# ============================================================

def parse_javascript_code(code):
    """
    Parse JavaScript source code using Tree-sitter.

    A new Parser instance is created for each file.
    """

    if not isinstance(code, str):
        raise TypeError(
            "JavaScript source code must be a string."
        )

    source_bytes = code.encode(
        "utf-8",
        errors="replace"
    )

    parser = Parser(
        JS_LANGUAGE
    )

    return parser.parse(
        source_bytes
    )


# ============================================================
# Get Node Text
# ============================================================

def get_node_text(node, source_code):
    """
    Return the exact source text represented by
    a Tree-sitter node.

    Tree-sitter uses UTF-8 byte offsets.
    """

    source_bytes = source_code.encode(
        "utf-8",
        errors="replace"
    )

    return source_bytes[
        node.start_byte:node.end_byte
    ].decode(
        "utf-8",
        errors="replace"
    )


# ============================================================
# Extract JavaScript Structure
# ============================================================

def extract_javascript_structure(
    tree,
    file_path,
    source_code
):
    """
    Extract useful structural information from
    JavaScript source code.

    Extracts:

        - functions
        - classes
        - methods
        - imports
        - exports
        - calls
        - variables
        - exceptions

    Functions and classes are returned as chunks.
    """

    functions = []
    classes = []

    root = tree.root_node

    # ========================================================
    # Helpers
    # ========================================================

    def node_text(node):
        return get_node_text(
            node,
            source_code
        )

    def line_range(node):

        return (
            node.start_point.row + 1,
            node.end_point.row + 1
        )

    def get_name(node):

        name_node = node.child_by_field_name(
            "name"
        )

        if name_node:

            return node_text(
                name_node
            )

        return None

    # ========================================================
    # Collect Imports / Exports
    # ========================================================

    imports = []
    exports = []

    def collect_file_metadata(node):

        if node.type == "import_statement":

            imports.append(
                node_text(node)
            )

        elif node.type == "export_statement":

            exports.append(
                node_text(node)
            )

        for child in node.children:

            collect_file_metadata(
                child
            )

    collect_file_metadata(
        root
    )

    imports = list(
        dict.fromkeys(
            imports
        )
    )

    exports = list(
        dict.fromkeys(
            exports
        )
    )

    # ========================================================
    # Analyze Node
    # ========================================================

    def analyze_node(node):

        calls = []
        exceptions = []
        variables = []

        stack = [node]

        while stack:

            current = stack.pop()

            # ------------------------------------------------
            # Function Calls
            # ------------------------------------------------

            if current.type == "call_expression":

                function_node = (
                    current.child_by_field_name(
                        "function"
                    )
                )

                if function_node:

                    calls.append(
                        node_text(
                            function_node
                        )
                    )

            # ------------------------------------------------
            # Exceptions
            # ------------------------------------------------

            elif current.type == "throw_statement":

                exceptions.append(
                    node_text(
                        current
                    )
                )

            elif current.type == "catch_clause":

                exceptions.append(
                    node_text(
                        current
                    )
                )

            # ------------------------------------------------
            # Variables
            # ------------------------------------------------

            elif current.type in {
                "lexical_declaration",
                "variable_declaration"
            }:

                variables.append(
                    node_text(
                        current
                    )
                )

            # ------------------------------------------------
            # Continue Traversal
            # ------------------------------------------------

            for child in current.children:

                stack.append(
                    child
                )

        return {

            "calls": list(
                dict.fromkeys(
                    calls
                )
            ),

            "exceptions": list(
                dict.fromkeys(
                    exceptions
                )
            ),

            "variables": list(
                dict.fromkeys(
                    variables
                )
            ),
        }

    # ========================================================
    # Create Function Chunk
    # ========================================================

    def create_function_chunk(
        node,
        function_name=None,
        class_name=None
    ):

        start_line, end_line = line_range(
            node
        )

        analysis = analyze_node(
            node
        )

        return {

            "content": node_text(
                node
            ),

            "file": str(
                file_path
            ),

            "language": "javascript",

            "type": "function",

            "class": class_name,

            "function": function_name,

            "start_line": start_line,

            "end_line": end_line,

            "imports": imports,

            "calls": analysis[
                "calls"
            ],

            "exceptions": analysis[
                "exceptions"
            ],

            "variables": analysis[
                "variables"
            ],
        }

    # ========================================================
    # Create Class Chunk
    # ========================================================

    def create_class_chunk(
        node,
        class_name
    ):

        start_line, end_line = line_range(
            node
        )

        analysis = analyze_node(
            node
        )

        return {

            "content": node_text(
                node
            ),

            "file": str(
                file_path
            ),

            "language": "javascript",

            "type": "class",

            "class": class_name,

            "function": None,

            "start_line": start_line,

            "end_line": end_line,

            "imports": imports,

            "calls": analysis[
                "calls"
            ],

            "exceptions": analysis[
                "exceptions"
            ],

            "variables": analysis[
                "variables"
            ],
        }

    # ========================================================
    # AST Traversal
    # ========================================================

    def walk(
        node,
        class_name=None
    ):

        # ----------------------------------------------------
        # Class Declaration
        # ----------------------------------------------------

        if node.type == "class_declaration":

            current_class = get_name(
                node
            )

            classes.append(
                create_class_chunk(
                    node,
                    current_class
                )
            )

            for child in node.children:

                walk(
                    child,
                    current_class
                )

            return

        # ----------------------------------------------------
        # Class Method
        # ----------------------------------------------------

        if node.type == "method_definition":

            function_name = get_name(
                node
            )

            functions.append(
                create_function_chunk(
                    node,
                    function_name,
                    class_name
                )
            )

            return

        # ----------------------------------------------------
        # Function Declaration
        # ----------------------------------------------------

        if node.type == "function_declaration":

            function_name = get_name(
                node
            )

            functions.append(
                create_function_chunk(
                    node,
                    function_name,
                    class_name
                )
            )

            return

        # ----------------------------------------------------
        # Function Expression
        # ----------------------------------------------------

        if node.type == "function_expression":

            functions.append(
                create_function_chunk(
                    node,
                    None,
                    class_name
                )
            )

            return

        # ----------------------------------------------------
        # Arrow Function
        # ----------------------------------------------------

        if node.type == "arrow_function":

            functions.append(
                create_function_chunk(
                    node,
                    None,
                    class_name
                )
            )

            return

        # ----------------------------------------------------
        # Continue Traversal
        # ----------------------------------------------------

        for child in node.children:

            walk(
                child,
                class_name
            )

    # ========================================================
    # Start AST Traversal
    # ========================================================

    walk(
        root
    )

    # ========================================================
    # Return
    # ========================================================

    return {

        "file": str(
            file_path
        ),

        "language": "javascript",

        "functions": functions,

        "classes": classes,

        "imports": imports,

        "exports": exports,
    }


# ============================================================
# Parse + Extract
# ============================================================

def parse_and_extract_javascript(
    code,
    file_path
):
    """
    Parse JavaScript source code and extract
    structural metadata.
    """

    tree = parse_javascript_code(
        code
    )

    return extract_javascript_structure(
        tree,
        file_path,
        code
    )


# ============================================================
# Standalone Test
# ============================================================

if __name__ == "__main__":

    test_code = """
import express from "express";

class OrderService {

    cancelOrder(orderId) {

        if (!orderId) {
            throw new Error("Order ID required");
        }

        return this.deleteOrder(orderId);
    }

    deleteOrder(id) {
        return db.delete(id);
    }
}

function createOrder(data) {
    return saveOrder(data);
}

const updateOrder = (id, data) => {
    return updateDatabase(id, data);
};

export default OrderService;
"""

    file_path = "test.js"

    print(
        "Parsing JavaScript..."
    )

    result = parse_and_extract_javascript(
        test_code,
        file_path
    )

    print(
        "\n=============================="
    )

    print(
        "PARSER SUCCESS"
    )

    print(
        "=============================="
    )

    print(
        "\nFile:",
        result["file"]
    )

    print(
        "Language:",
        result["language"]
    )

    print(
        "\nImports:"
    )

    for item in result["imports"]:

        print(
            item
        )

    print(
        "\nExports:"
    )

    for item in result["exports"]:

        print(
            item
        )

    print(
        "\nClasses:"
    )

    for item in result["classes"]:

        print(
            "Class:",
            item["class"]
        )

        print(
            "Lines:",
            item["start_line"],
            "-",
            item["end_line"]
        )

    print(
        "\nFunctions:"
    )

    for item in result["functions"]:

        print(
            "\nFunction:",
            item["function"]
        )

        print(
            "Class:",
            item["class"]
        )

        print(
            "Lines:",
            item["start_line"],
            "-",
            item["end_line"]
        )

        print(
            "Calls:",
            item["calls"]
        )

        print(
            "Exceptions:",
            item["exceptions"]
        )

        print(
            "Variables:",
            item["variables"]
        )

    print(
        "\n=============================="
    )

    print(
        "DONE"
    )

    print(
        "=============================="
    )