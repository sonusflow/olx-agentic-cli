"""Categories & attributes for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any, Optional

from olx_api.client import OLXClient


class Categories:
    """Browse the OLX category tree and its attributes."""

    def __init__(self, client: OLXClient):
        self._c = client

    def list(self, parent_id: Optional[int] = None) -> dict[str, Any]:
        """List categories, optionally filtering by parent.

        Args:
            parent_id: If given, list only direct children of this category.

        Returns:
            Parsed JSON with category list.
        """
        params: dict[str, Any] = {}
        if parent_id is not None:
            params["parent_id"] = parent_id
        return self._c.get("/categories", params=params)

    def get(self, category_id: int) -> dict[str, Any]:
        """Get a single category's details.

        Args:
            category_id: The numeric category ID.

        Returns:
            Parsed JSON with category details.
        """
        return self._c.get(f"/categories/{category_id}")

    def attributes(self, category_id: int) -> dict[str, Any]:
        """Get attributes (fields) required for a category.

        Args:
            category_id: The numeric category ID.

        Returns:
            Parsed JSON with attribute definitions.
        """
        return self._c.get(f"/categories/{category_id}/attributes")

    def suggest(self, query: str) -> dict[str, Any]:
        """Search categories by name."""
        return self._c.get("/categories/suggestion", params={"q": query})
