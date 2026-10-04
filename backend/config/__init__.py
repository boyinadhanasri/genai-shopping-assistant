"""
ShopAI Configuration Package
Exposes category flow rules and budget tiers.
"""

from backend.config.category_budget_rules import (
    CATEGORY_BUDGET_TIERS,
    get_budget_options_for_category,
    parse_budget_from_option,
)
from backend.config.category_flow_rules import (
    SHOPPING_WELCOME_FLOW,
    CATEGORY_SHOPPING_FLOWS,
    normalize_category_name,
    get_flow_for_category,
)

__all__ = [
    "CATEGORY_BUDGET_TIERS",
    "get_budget_options_for_category",
    "parse_budget_from_option",
    "SHOPPING_WELCOME_FLOW",
    "CATEGORY_SHOPPING_FLOWS",
    "normalize_category_name",
    "get_flow_for_category",
]
