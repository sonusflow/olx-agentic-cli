"""Adverts CRUD operations for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any, Optional

from olx_api.client import OLXClient


class Adverts:
    """Manage OLX adverts (listings)."""

    def __init__(self, client: OLXClient):
        self._c = client

    def list(
        self,
        offset: int = 0,
        limit: int = 10,
        sort_by: str = "created_at:desc",
    ) -> dict[str, Any]:
        """List the authenticated user's adverts.

        Args:
            offset: Pagination offset.
            limit: Number of results per page (max 50).
            sort_by: Sort expression, e.g. 'created_at:desc'.

        Returns:
            Parsed JSON with 'data' list and pagination metadata.
        """
        return self._c.get(
            "/adverts",
            params={"offset": offset, "limit": limit, "sort_by": sort_by},
        )

    def get(self, advert_id: int) -> dict[str, Any]:
        """Get details for a single advert.

        Args:
            advert_id: The numeric advert ID.

        Returns:
            Parsed JSON with advert details.
        """
        return self._c.get(f"/adverts/{advert_id}")

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a new advert.

        Args:
            payload: Full advert body as expected by the API.

        Returns:
            Parsed JSON with the created advert.
        """
        return self._c.post("/adverts", json=payload)

    def update(self, advert_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Update an existing advert.

        Args:
            advert_id: The numeric advert ID.
            payload: Fields to update.

        Returns:
            Parsed JSON with the updated advert.
        """
        return self._c.put(f"/adverts/{advert_id}", json=payload)

    def delete(self, advert_id: int) -> None:
        """Delete (deactivate) an advert.

        Args:
            advert_id: The numeric advert ID.
        """
        self._c.delete(f"/adverts/{advert_id}")

    def activate(self, advert_id: int) -> dict[str, Any]:
        """Activate a draft or deactivated advert.

        Args:
            advert_id: The numeric advert ID.

        Returns:
            Parsed JSON confirmation.
        """
        return self._c.post(f"/adverts/{advert_id}/commands", json={"command": "activate"})

    def deactivate(self, advert_id: int) -> dict[str, Any]:
        """Deactivate an active advert."""
        return self._c.post(f"/adverts/{advert_id}/commands", json={"command": "deactivate"})

    def finish(self, advert_id: int) -> dict[str, Any]:
        """Mark an advert as finished (sold)."""
        return self._c.post(f"/adverts/{advert_id}/commands", json={"command": "finish"})

    def extend(self, advert_id: int) -> dict[str, Any]:
        """Extend an advert's validity period."""
        return self._c.post(f"/adverts/{advert_id}/commands", json={"command": "extend"})

    def statistics(self, advert_id: int) -> dict[str, Any]:
        """Get advert statistics (views, phone views, observers)."""
        return self._c.get(f"/adverts/{advert_id}/statistics")

    def moderation_reason(self, advert_id: int) -> dict[str, Any]:
        """Get moderation rejection reason for an advert."""
        return self._c.get(f"/adverts/{advert_id}/moderation-reason")
