"""Web search server tool for the agent framework."""

from dataclasses import dataclass
from typing import Any


@dataclass
class WebSearchServerTool:
    """Web search server tool that uses Anthropic's server tool format."""

    name: str = "web_search"
    type: str = "web_search_20250305"
    max_uses: int | None = None
    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None
    user_location: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to Anthropic server tool format."""
        tool_dict: dict[str, Any] = {
            "type": self.type,
            "name": self.name,
        }

        # Add optional parameters if provided
        if self.max_uses is not None:
            tool_dict["max_uses"] = self.max_uses

        if self.allowed_domains is not None:
            tool_dict["allowed_domains"] = self.allowed_domains

        if self.blocked_domains is not None:
            tool_dict["blocked_domains"] = self.blocked_domains

        if self.user_location is not None:
            tool_dict["user_location"] = self.user_location

        return tool_dict
