def build_context(results):

    context_parts = []

    for result in results:

        metadata = result["metadata"]

        context = f"""
File: {metadata.get("file")}
Function: {metadata.get("function")}
Lines: {metadata.get("start_line")} - {metadata.get("end_line")}

Code:
{result["content"]}
"""

        context_parts.append(context)

    return "\n\n".join(context_parts)