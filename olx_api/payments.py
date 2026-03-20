"""Payments, paid features, and promotion packets for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any

from olx_api.client import OLXClient


class Payments:
    """Manage paid features, promotion packets, and payment history."""

    def __init__(self, client: OLXClient):
        self._c = client

    # -- Paid features --------------------------------------------------

    def list_paid_features(self, advert_id: int) -> dict[str, Any]:
        """List paid features available for an advert.

        Args:
            advert_id: The numeric advert ID.

        Returns:
            Parsed JSON with available paid features.
        """
        return self._c.get(f"/adverts/{advert_id}/paid-features")

    def apply_paid_feature(self, advert_id: int, feature: str) -> dict[str, Any]:
        """Apply a paid feature to an advert.

        Args:
            advert_id: The numeric advert ID.
            feature: Feature identifier (e.g. 'promote', 'urgent', 'top_ad').

        Returns:
            Parsed JSON confirmation.
        """
        return self._c.post(
            f"/adverts/{advert_id}/paid-features",
            json={"feature": feature},
        )

    # -- Promotion packets ----------------------------------------------

    def list_packets(self) -> dict[str, Any]:
        """List available promotion packets.

        Returns:
            Parsed JSON with packet list.
        """
        return self._c.get("/packets")

    # -- Payment history ------------------------------------------------

    def list_payments(self, offset: int = 0, limit: int = 20) -> dict[str, Any]:
        """List the user's payment history.

        Args:
            offset: Pagination offset.
            limit: Results per page.

        Returns:
            Parsed JSON with payment history.
        """
        return self._c.get("/payments", params={"offset": offset, "limit": limit})

    def list_all_features(self) -> dict[str, Any]:
        """List all available paid feature types."""
        return self._c.get("/paid-features")

    def apply_packet(self, advert_id: int, payment_method: str = "account") -> dict[str, Any]:
        """Apply a promotion packet to an advert."""
        return self._c.post(f"/adverts/{advert_id}/packets", json={"payment_method": payment_method})
