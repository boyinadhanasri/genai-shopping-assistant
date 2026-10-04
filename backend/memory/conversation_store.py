"""
Conversational Memory & User Session Store for GenAI Shopping Assistant
Tracks multi-turn preferences, category flow progress, brand affinity, and past views.

Features:
- Maintains context across follow-ups:
  Turn 1: "Show Samsung phones" -> stores brand=Samsung, category=Smartphones
  Turn 2: "Show camera phones" -> preserves brand=Samsung, adds priority=Camera
- Manages dynamic multi-step shopping flows (Home & Kitchen, Books, Sports, Smartphones, Laptops, Shoes, Fashion, Beauty, Audio)
"""

import re
import sys
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.config.category_flow_rules import (
    CATEGORY_SHOPPING_FLOWS,
    normalize_category_name,
)
from backend.config.category_budget_rules import parse_budget_from_option

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class ChatEntry(BaseModel):
    role: str
    content: str
    timestamp: float = Field(default_factory=time.time)


class UserPreferences(BaseModel):
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    budget: Optional[float] = None
    pending_budget: Optional[float] = None
    purpose: Optional[str] = None
    priority: Optional[str] = None
    gender: Optional[str] = None
    active_flow_category: Optional[str] = None
    active_flow_step: int = 0
    awaiting_product_type: bool = False
    pending_clarification: bool = False
    min_rating: Optional[float] = None
    constraints: List[str] = Field(default_factory=list)
    product_topic: Optional[str] = None
    viewed_product_ids: List[str] = Field(default_factory=list)


class UserSession(BaseModel):
    user_id: str
    chat_history: List[ChatEntry] = Field(default_factory=list)
    search_history: List[str] = Field(default_factory=list)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    last_active: float = Field(default_factory=time.time)


class ConversationMemoryStore:
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}

    def get_session(self, user_id: str) -> UserSession:
        if not user_id:
            user_id = "default_shopper"
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(user_id=user_id)
        self._sessions[user_id].last_active = time.time()
        return self._sessions[user_id]

    def add_message(self, user_id: str, role: str, content: str):
        session = self.get_session(user_id)
        session.chat_history.append(ChatEntry(role=role, content=content))
        if len(session.chat_history) > 30:
            session.chat_history = session.chat_history[-30:]

    def add_search_query(self, user_id: str, query: str):
        session = self.get_session(user_id)
        session.search_history.append(query)
        if len(session.search_history) > 30:
            session.search_history = session.search_history[-30:]

    def sync_from_history(self, user_id: str, history: Optional[List[Any]] = None):
        """Fail-safe recovery from client chat history if session state is missing."""
        if not history:
            return
        session = self.get_session(user_id)
        prefs = session.preferences
        if prefs.budget is not None and not (prefs.awaiting_product_type or prefs.pending_clarification):
            return

        for item in reversed(history):
            content = getattr(item, "content", None) or (item.get("content") if isinstance(item, dict) else "")
            role = getattr(item, "role", None) or (item.get("role") if isinstance(item, dict) else "")
            if not content:
                continue

            if role == "assistant" and any(k in content.lower() for k in ["what type of", "what are you looking for", "target budget", "select your budget"]):
                prefs.awaiting_product_type = True
                prefs.pending_clarification = True

            if role == "user":
                from backend.ai.query_understanding import rule_based_query_understanding
                extracted = rule_based_query_understanding(content)
                if extracted.get("budget") and prefs.budget is None:
                    prefs.budget = float(extracted["budget"])
                    prefs.pending_budget = float(extracted["budget"])
                if extracted.get("category") and prefs.category is None:
                    prefs.category = extracted["category"]
                if extracted.get("subcategory") and prefs.subcategory is None:
                    prefs.subcategory = extracted["subcategory"]
                if extracted.get("brand") and prefs.brand is None:
                    prefs.brand = extracted["brand"]
                if prefs.budget is not None and prefs.subcategory is not None:
                    break

    def update_preferences_from_query(self, user_id: str, parsed: Dict[str, Any]) -> UserPreferences:
        """
        Updates session preferences intelligently based on turn intent, flow step, and slot extractions.
        Maintains conversational state across follow-up turns.
        """
        session = self.get_session(user_id)
        prefs = session.preferences
        query_text = (parsed.get("raw_query") or "").lower().strip()

        # Reset trigger
        if any(w in query_text for w in ["reset", "clear context", "start over", "new search", "restart"]):
            session.preferences = UserPreferences()
            return session.preferences

        parsed_budget = parse_budget_from_option(query_text) or parsed.get("budget")

        # Category switch check
        new_cat = parsed.get("category")
        if new_cat and new_cat != "General":
            norm_new_cat = normalize_category_name(new_cat)
            if prefs.category and normalize_category_name(prefs.category) != norm_new_cat:
                # Switched category: reset category-specific filters
                if not parsed.get("brand"):
                    prefs.brand = None
                if parsed.get("budget") is None:
                    prefs.budget = None
                prefs.subcategory = None
                prefs.purpose = None
                prefs.priority = None
                prefs.gender = None
                prefs.active_flow_step = 0
            prefs.category = norm_new_cat

        # Subcategory updates
        if parsed.get("subcategory"):
            prefs.subcategory = parsed["subcategory"]
            prefs.awaiting_product_type = False
            prefs.pending_clarification = False

        # Brand updates (e.g. "Show Prestige cookers" -> brand="Prestige")
        if parsed.get("brand"):
            prefs.brand = parsed["brand"]

        # Budget updates
        if parsed_budget is not None:
            prefs.budget = float(parsed_budget)
            prefs.pending_budget = None

        # Purpose & Priority updates
        if parsed.get("purpose"):
            prefs.purpose = parsed["purpose"]
        if parsed.get("priority"):
            prefs.priority = parsed["priority"]
        if parsed.get("gender"):
            prefs.gender = parsed["gender"]

        # Rating updates
        if any(phrase in query_text for phrase in ["higher rating", "better rating", "best rating", "top rated", "high rating", "4.5+"]):
            prefs.min_rating = 4.5
        elif any(phrase in query_text for phrase in ["4 star", "rated 4", "good rating"]):
            prefs.min_rating = 4.0

        # Feature constraints
        for c in parsed.get("constraints", []):
            if c not in prefs.constraints:
                prefs.constraints.append(c)

        return prefs

    def get_effective_parameters(self, user_id: str, parsed: Dict[str, Any], history: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Merges current query extractions with accumulated conversation preferences.
        """
        session = self.get_session(user_id)
        if history:
            self.sync_from_history(user_id, history)
        prefs = self.update_preferences_from_query(user_id, parsed)

        # Build compound search query text reflecting conversation context
        effective_query_tokens = []
        if prefs.brand:
            effective_query_tokens.append(prefs.brand)
        if prefs.gender and prefs.category in ["Fashion", "Shoes"]:
            effective_query_tokens.append(prefs.gender)
        if prefs.priority:
            effective_query_tokens.append(prefs.priority)
        if prefs.purpose:
            effective_query_tokens.append(prefs.purpose)
        if prefs.subcategory:
            effective_query_tokens.append(prefs.subcategory)
        elif prefs.product_topic:
            effective_query_tokens.append(prefs.product_topic)

        compound_query = " ".join(effective_query_tokens).strip()
        if not compound_query:
            compound_query = parsed.get("raw_query") or (prefs.category or "products")

        # Determine category flow progression if user is in an active flow
        norm_cat = normalize_category_name(prefs.category)
        flow_cfg = CATEGORY_SHOPPING_FLOWS.get(norm_cat)

        next_flow_question = None
        next_flow_options = []
        flow_in_progress = False

        if flow_cfg and not parsed.get("compare_targets"):
            if norm_cat == "Home & Kitchen":
                if not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

            elif norm_cat == "Books":
                if not prefs.purpose and not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

            elif norm_cat == "Sports":
                if not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

            elif norm_cat == "Laptops":
                if not prefs.purpose and not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

            elif norm_cat == "Smartphones":
                if not prefs.priority and not (parsed.get("subcategory") and parsed.get("brand")):
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

            elif norm_cat in ["Shoes", "Fashion"]:
                if not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    budget_step_idx = 1 if len(flow_cfg["steps"]) == 2 else 2
                    next_flow_question = flow_cfg["steps"][budget_step_idx]["question"]
                    next_flow_options = flow_cfg["steps"][budget_step_idx]["options"]

            elif norm_cat == "Beauty":
                if not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][2]["question"]
                    next_flow_options = flow_cfg["steps"][2]["options"]

            elif norm_cat == "Audio":
                if not prefs.subcategory:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][0]["question"]
                    next_flow_options = flow_cfg["steps"][0]["options"]
                elif prefs.budget is None:
                    flow_in_progress = True
                    next_flow_question = flow_cfg["steps"][1]["question"]
                    next_flow_options = flow_cfg["steps"][1]["options"]

        return {
            "query": compound_query,
            "category": prefs.category,
            "subcategory": prefs.subcategory,
            "brand": prefs.brand,
            "budget": prefs.budget,
            "purpose": prefs.purpose,
            "priority": prefs.priority,
            "gender": prefs.gender,
            "min_rating": prefs.min_rating,
            "constraints": prefs.constraints,
            "intent": parsed.get("intent", "product_search"),
            "compare_targets": parsed.get("compare_targets", []),
            "flow_in_progress": flow_in_progress,
            "flow_question": next_flow_question,
            "flow_options": next_flow_options,
        }


# Global store instance
conversation_store = ConversationMemoryStore()
