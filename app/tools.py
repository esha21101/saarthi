from app.models import AddressBody, BlockCardBody, HandoffBody, StatementBody


def schema_of(model):
    """JSON schema for a Pydantic model, without the noisy 'title' keys."""

    def strip(node):
        if isinstance(node, dict):
            return {k: strip(v) for k, v in node.items() if k != "title"}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    return strip(model.model_json_schema())


def tool(name, description, parameters):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


NO_PARAMS = {"type": "object", "properties": {}}

TOOLS = [
    # Written by hand on purpose: the backend's VerifyBody also takes a phone
    # number, but the agent supplies that from caller ID. The LLM only gets dob.
    tool(
        "verify_identity",
        "Verify the caller by their date of birth. Must succeed before any "
        "other tool is used.",
        {
            "type": "object",
            "properties": {
                "dob": {
                    "type": "string",
                    "description": "Caller's date of birth in YYYY-MM-DD format",
                }
            },
            "required": ["dob"],
        },
    ),
    tool(
        "get_loans",
        "List the verified caller's loans with balance, EMI and due date.",
        NO_PARAMS,
    ),
    tool(
        "send_statement",
        "Email a loan statement to the caller's registered email.",
        schema_of(StatementBody),
    ),
    tool("block_card", "Block the caller's card.", schema_of(BlockCardBody)),
    tool(
        "update_address",
        "Update the caller's registered address. Read the new address back first.",
        schema_of(AddressBody),
    ),
    tool(
        "transfer_to_human",
        "Hand the call to a human agent. Use when the caller asks for one, or "
        "when the request is outside what you can do.",
        schema_of(HandoffBody),
    ),
]