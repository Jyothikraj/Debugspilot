def build_context(results):
    context_parts = []

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]

        if rank == 1:
            label = "PRIMARY RELEVANT CODE"
        else:
            label = "ADDITIONAL RETRIEVED CODE"

        context = f"""
{label}

File: {metadata.get("file")}
Class: {metadata.get("class")}
Function: {metadata.get("function")}
Lines: {metadata.get("start_line")} - {metadata.get("end_line")}

Code:
{result["content"]}
"""

        context_parts.append(context)

    return "\n\n".join(context_parts)