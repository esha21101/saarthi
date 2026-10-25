TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "verify_identity",
            "description": (
                "Verify the caller by their date of birth. Must succeed before "
                "any other tool is used."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dob": {
                        "type": "string",
                        "description": "Caller's date of birth in YYYY-MM-DD format",
                    }
                },
                "required": ["dob"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_loans",
            "description": "List the verified caller's loans with balance, EMI and due date.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_statement",
            "description": (
                "Email a loan statement to the caller's registered email. Only set "
                "confirmed to true after the caller has clearly agreed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "loan_id": {"type": "integer"},
                    "period": {
                        "type": "string",
                        "enum": ["last_month", "last_3_months", "last_6_months"],
                    },
                    "confirmed": {"type": "boolean"},
                },
                "required": ["loan_id", "period", "confirmed"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "block_card",
            "description": (
                "Block the caller's card. Only set confirmed to true after the "
                "caller has clearly agreed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "enum": ["lost", "stolen", "fraud_suspected", "other"],
                    },
                    "confirmed": {"type": "boolean"},
                },
                "required": ["reason", "confirmed"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_address",
            "description": (
                "Update the caller's registered address. Read the new address back "
                "first, and only set confirmed to true after the caller agrees."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "new_address": {"type": "string"},
                    "confirmed": {"type": "boolean"},
                },
                "required": ["new_address", "confirmed"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_human",
            "description": (
                "Hand the call to a human agent. Use when the caller asks for one, "
                "or when the request is outside what you can do."
            ),
            "parameters": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
]