# Defines the allowed claim status progression (BR-003)
CLAIM_WORKFLOW_ORDER = [
    "submitted",
    "validation",
    "assigned",
    "under_review",
    "approved",   # or "rejected"
    "closed",
]

TERMINAL_STATUSES = {"approved", "rejected", "closed"}


def validate_transition(current_status: str, new_status: str, is_override: bool = False) -> str | None:
    """
    Returns an error message if the transition is invalid, otherwise returns None.
    """
    if is_override:
        return None  # Manager override bypasses the forward-only rule

    if new_status not in CLAIM_WORKFLOW_ORDER and new_status != "rejected":
        return f"'{new_status}' is not a recognized claim status"

    try:
        current_index = CLAIM_WORKFLOW_ORDER.index(current_status)
    except ValueError:
        return f"Current status '{current_status}' is not recognized"

    # Special case: rejected can happen from under_review onward
    if new_status == "rejected":
        if current_index < CLAIM_WORKFLOW_ORDER.index("under_review"):
            return "Claim must be under review before it can be rejected"
        return None

    new_index = CLAIM_WORKFLOW_ORDER.index(new_status)

    if new_index < current_index:
        return (
            f"Invalid transition: '{current_status}' -> '{new_status}'. "
            "Status can only move forward unless a Manager override is used."
        )

    return None