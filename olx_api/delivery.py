"""Delivery endpoints for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any

from olx_api.client import OLXClient


class Delivery:
    """Manage delivery methods and shipment info."""

    def __init__(self, client: OLXClient):
        self._c = client

    def list_methods(self) -> dict[str, Any]:
        """List available delivery methods.

        Returns:
            Parsed JSON with delivery method list.
        """
        return self._c.get("/delivery/methods")

    def get_shipment(self, advert_id: int) -> dict[str, Any]:
        """Get shipment information for an advert.

        Args:
            advert_id: The numeric advert ID.

        Returns:
            Parsed JSON with shipment details.
        """
        return self._c.get(f"/adverts/{advert_id}/shipment")

    def create_shipment(self, advert_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a shipment for a sold advert.

        Args:
            advert_id: The numeric advert ID.
            payload: Shipment details (method, dimensions, etc.).

        Returns:
            Parsed JSON with created shipment.
        """
        return self._c.post(f"/adverts/{advert_id}/shipment", json=payload)
