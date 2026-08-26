import ast
from pathlib import Path


def parse_python_code(code):
    """
    Parse Python source code into an Abstract Syntax Tree.
    """
    return ast.parse(code)


def get_source(code, node):
    """
    Extract the exact source code represented by an AST node.
    """
    lines = code.splitlines()

    if not hasattr(node, "lineno"):
        return ""

    start = node.lineno - 1
    end = getattr(node, "end_lineno", node.lineno)

    return "\n".join(lines[start:end])


def get_decorators(node):
    """
    Extract decorators such as:
        @app.get("/users")
        @login_required
    """
    decorators = []

    for decorator in getattr(node, "decorator_list", []):
        decorators.append(ast.unparse(decorator))

    return decorators


def get_arguments(node):
    """
    Extract function arguments.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return []

    arguments = []

    args = node.args

    # Positional + positional-only arguments
    positional_args = args.posonlyargs + args.args

    for arg in positional_args:
        arguments.append({
            "name": arg.arg,
            "annotation": ast.unparse(arg.annotation)
            if arg.annotation else None
        })

    # *args
    if args.vararg:
        arguments.append({
            "name": args.vararg.arg,
            "annotation": ast.unparse(args.vararg.annotation)
            if args.vararg.annotation else None
        })

    # Keyword-only arguments
    for arg in args.kwonlyargs:
        arguments.append({
            "name": arg.arg,
            "annotation": ast.unparse(arg.annotation)
            if arg.annotation else None
        })

    # **kwargs
    if args.kwarg:
        arguments.append({
            "name": args.kwarg.arg,
            "annotation": ast.unparse(args.kwarg.annotation)
            if args.kwarg.annotation else None
        })

    return arguments


def get_return_type(node):
    """
    Extract function return annotation.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None

    if node.returns:
        return ast.unparse(node.returns)

    return None


def get_imports(tree):
    """
    Extract import statements.
    """
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.append({
                    "type": "import",
                    "module": alias.name,
                    "name": alias.asname,
                    "line": node.lineno
                })

        elif isinstance(node, ast.ImportFrom):

            for alias in node.names:
                imports.append({
                    "type": "from_import",
                    "module": node.module,
                    "name": alias.name,
                    "alias": alias.asname,
                    "line": node.lineno
                })

    return imports


def get_function_calls(node):
    """
    Extract function/method calls inside a function or method.

    Example:
        db.get_user()
        validate_user()
    """
    calls = []

    for child in ast.walk(node):

        if isinstance(child, ast.Call):

            try:
                call_name = ast.unparse(child.func)
            except Exception:
                call_name = None

            if call_name:
                calls.append({
                    "name": call_name,
                    "line": child.lineno
                })

    return calls


def get_exceptions(node):
    """
    Extract exception handling information.
    """
    exceptions = []

    for child in ast.walk(node):

        if isinstance(child, ast.Raise):

            exception_name = None

            if child.exc:
                try:
                    exception_name = ast.unparse(child.exc)
                except Exception:
                    pass

            exceptions.append({
                "type": "raise",
                "exception": exception_name,
                "line": child.lineno
            })

        elif isinstance(child, ast.ExceptHandler):

            exception_name = None

            if child.type:
                try:
                    exception_name = ast.unparse(child.type)
                except Exception:
                    pass

            exceptions.append({
                "type": "except",
                "exception": exception_name,
                "line": child.lineno
            })

    return exceptions


def get_variables(node):
    """
    Extract assignments inside a function/class/module.
    """
    variables = []

    for child in ast.walk(node):

        if isinstance(child, ast.Assign):

            for target in child.targets:

                try:
                    name = ast.unparse(target)
                except Exception:
                    name = None

                if name:
                    variables.append({
                        "name": name,
                        "line": child.lineno
                    })

        elif isinstance(child, ast.AnnAssign):

            try:
                name = ast.unparse(child.target)
            except Exception:
                name = None

            if name:
                variables.append({
                    "name": name,
                    "line": child.lineno
                })

    return variables


def extract_function_info(
    node,
    file_path,
    source_code,
    class_name=None
):
    """
    Convert a Python function/method AST node
    into normalized metadata.
    """

    function_type = (
        "async_function"
        if isinstance(node, ast.AsyncFunctionDef)
        else "function"
    )

    return {
        "type": function_type,

        "file": str(file_path),

        "language": "python",

        "class": class_name,

        "function": node.name,

        "content": get_source(source_code, node),

        "start_line": node.lineno,

        "end_line": getattr(
            node,
            "end_lineno",
            node.lineno
        ),

        "arguments": get_arguments(node),

        "return_type": get_return_type(node),

        "decorators": get_decorators(node),

        "calls": get_function_calls(node),

        "exceptions": get_exceptions(node),

        "variables": get_variables(node),
    }


def extract_class_info(
    node,
    file_path,
    source_code
):
    """
    Extract class-level information.
    """

    methods = []

    for child in node.body:

        if isinstance(
            child,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            methods.append(
                extract_function_info(
                    child,
                    file_path,
                    source_code,
                    class_name=node.name
                )
            )

    return {
        "type": "class",

        "file": str(file_path),

        "language": "python",

        "class": node.name,

        "content": get_source(
            source_code,
            node
        ),

        "start_line": node.lineno,

        "end_line": getattr(
            node,
            "end_lineno",
            node.lineno
        ),

        "bases": [
            ast.unparse(base)
            for base in node.bases
        ],

        "decorators": get_decorators(node),

        "methods": methods
    }


def extract_routes(tree):
    """
    Detect common FastAPI / Flask-style route decorators.

    Examples:

        @app.get("/users")
        @router.post("/orders")
    """

    routes = []

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue

        for decorator in node.decorator_list:

            if not isinstance(
                decorator,
                ast.Call
            ):
                continue

            func = decorator.func

            if not isinstance(
                func,
                ast.Attribute
            ):
                continue

            method = func.attr

            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head"
            }:
                continue

            route_path = None

            if decorator.args:

                try:
                    route_path = ast.literal_eval(
                        decorator.args[0]
                    )
                except Exception:
                    pass

            routes.append({
                "type": "route",

                "file": None,

                "language": "python",

                "function": node.name,

                "method": method.upper(),

                "path": route_path,

                "start_line": node.lineno,

                "end_line": getattr(
                    node,
                    "end_lineno",
                    node.lineno
                )
            })

    return routes


def extract_python_structure(
    tree,
    file_path,
    source_code
):
    """
    Main extraction function.

    Returns semantic information useful
    for code intelligence and debugging.
    """

    functions = []
    classes = []

    for node in tree.body:

        # Top-level functions
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            functions.append(
                extract_function_info(
                    node,
                    file_path,
                    source_code
                )
            )

        # Classes
        elif isinstance(
            node,
            ast.ClassDef
        ):

            classes.append(
                extract_class_info(
                    node,
                    file_path,
                    source_code
                )
            )

    imports = get_imports(tree)

    routes = extract_routes(tree)

    return {
        "file": str(file_path),

        "language": "python",

        "classes": classes,

        "functions": functions,

        "imports": imports,

        "routes": routes
    }


# --------------------------------------------------
# Example usage
# --------------------------------------------------

if __name__ == "__main__":

    file_path = "test_project/app/main.py"

    source_code = Path(
        file_path
    ).read_text(
        encoding="utf-8"
    )

    tree = parse_python_code(
        source_code
    )

    result = extract_python_structure(
        tree,
        file_path,
        source_code
    )

    from pprint import pprint

    pprint(result)