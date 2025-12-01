"""
Business logic and validation rules for FixIt Tech Solutions.
Contains status transition rules, validation functions, and business constraints.
"""

from typing import List, Optional
from app.models import TicketStatus


# Define valid status transitions
VALID_STATUS_TRANSITIONS = {
    TicketStatus.PENDING: [
        TicketStatus.DIAGNOSED,
        TicketStatus.IN_PROGRESS,
        TicketStatus.CANCELLED
    ],
    TicketStatus.DIAGNOSED: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_PARTS,
        TicketStatus.COMPLETED,
        TicketStatus.READY_PICKUP,
        TicketStatus.CANCELLED
    ],
    TicketStatus.IN_PROGRESS: [
        TicketStatus.WAITING_PARTS,
        TicketStatus.COMPLETED,
        TicketStatus.READY_PICKUP,
        TicketStatus.CANCELLED
    ],
    TicketStatus.WAITING_PARTS: [
        TicketStatus.IN_PROGRESS,
        TicketStatus.CANCELLED
    ],
    TicketStatus.COMPLETED: [
        TicketStatus.READY_PICKUP,
        TicketStatus.DELIVERED
    ],
    TicketStatus.READY_PICKUP: [
        TicketStatus.DELIVERED,
        TicketStatus.IN_PROGRESS  # Customer wants additional work
    ],
    TicketStatus.DELIVERED: [],  # Final state
    TicketStatus.CANCELLED: []   # Final state
}


def is_valid_status_transition(
    current_status: TicketStatus,
    new_status: TicketStatus
) -> bool:
    """
    Check if a status transition is valid according to business rules.
    
    Args:
        current_status: The current status of the ticket
        new_status: The desired new status
        
    Returns:
        True if the transition is allowed, False otherwise
    """
    if current_status == new_status:
        return True  # No change is always valid
    
    valid_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in valid_transitions


def get_valid_next_statuses(current_status: TicketStatus) -> List[TicketStatus]:
    """
    Get all valid next statuses for a given current status.
    
    Args:
        current_status: The current status of the ticket
        
    Returns:
        List of valid next statuses
    """
    return VALID_STATUS_TRANSITIONS.get(current_status, [])


def validate_status_transition(
    current_status: TicketStatus,
    new_status: TicketStatus
) -> Optional[str]:
    """
    Validate a status transition and return an error message if invalid.
    
    Args:
        current_status: The current status of the ticket
        new_status: The desired new status
        
    Returns:
        None if valid, error message string if invalid
    """
    if not is_valid_status_transition(current_status, new_status):
        valid_next = get_valid_next_statuses(current_status)
        if not valid_next:
            return f"Ticket in '{current_status.value}' status cannot be changed (final state)"
        
        valid_list = ", ".join([s.value for s in valid_next])
        return f"Cannot transition from '{current_status.value}' to '{new_status.value}'. Valid next statuses: {valid_list}"
    
    return None


def validate_priority(priority: str) -> bool:
    """
    Validate if a priority value is allowed.
    
    Args:
        priority: Priority string to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_priorities = ["low", "normal", "high", "urgent"]
    return priority.lower() in valid_priorities


def get_priority_weight(priority: str) -> int:
    """
    Get numeric weight for priority (for sorting/filtering).
    
    Args:
        priority: Priority string
        
    Returns:
        Numeric weight (higher = more urgent)
    """
    weights = {
        "low": 1,
        "normal": 2,
        "high": 3,
        "urgent": 4
    }
    return weights.get(priority.lower(), 2)


def is_ticket_actionable(status: TicketStatus) -> bool:
    """
    Check if a ticket in the given status can still be worked on.
    
    Args:
        status: Ticket status to check
        
    Returns:
        True if ticket is still actionable, False if in final state
    """
    final_states = [TicketStatus.DELIVERED, TicketStatus.CANCELLED]
    return status not in final_states


def estimate_cost_range(device_type: str, issue_keywords: List[str]) -> tuple:
    """
    Provide a rough cost estimate range based on device type and issue.
    This is a simplified heuristic for demonstration purposes.
    
    Args:
        device_type: Type of device (phone, laptop, etc.)
        issue_keywords: Keywords from issue description
        
    Returns:
        Tuple of (min_cost, max_cost)
    """
    base_costs = {
        "phone": (50, 300),
        "laptop": (100, 500),
        "tablet": (75, 350),
        "desktop": (150, 600),
        "watch": (30, 200),
        "other": (50, 400)
    }
    
    min_cost, max_cost = base_costs.get(device_type.lower(), (50, 400))
    
    # Adjust for severity indicators
    severity_keywords = ["cracked", "broken", "dead", "not working", "damaged"]
    if any(keyword in " ".join(issue_keywords).lower() for keyword in severity_keywords):
        min_cost = int(min_cost * 1.2)
        max_cost = int(max_cost * 1.3)
    
    return (min_cost, max_cost)
