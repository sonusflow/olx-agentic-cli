"""User endpoints for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any

from olx_api.client import OLXClient


class Users:
    """Access OLX user information."""

    def __init__(self, client: OLXClient):
        self._c = client

    def me(self) -> dict[str, Any]:
        """Get the authenticated user's profile.

        Returns:
            Parsed JSON with user details (id, email, name, phone, etc.).
        """
        return self._c.get("/users/me")

    def get(self, user_id: int) -> dict[str, Any]:
        """Get a public user profile.

        Args:
            user_id: The numeric user ID.

        Returns:
            Parsed JSON with public user information.
        """
        return self._c.get(f"/users/{user_id}")

    def account_balance(self) -> dict[str, Any]:
        """Get the authenticated user's account balance."""
        return self._c.get("/users/me/account-balance")

    def payment_methods(self) -> dict[str, Any]:
        """Get available payment methods."""
        return self._c.get("/users/me/payment-methods")

    def billing(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Get billing transaction history."""
        return self._c.get("/users/me/billing", params={"page": page, "limit": limit})

    def prepaid_invoices(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Get prepaid invoices."""
        return self._c.get("/users/me/prepaid-invoices", params={"page": page, "limit": limit})

    def postpaid_invoices(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Get postpaid invoices."""
        return self._c.get("/users/me/postpaid-invoices", params={"page": page, "limit": limit})

    def list_packets(self, offset: int = 0, limit: int = 20) -> dict[str, Any]:
        """List bought promotion packets."""
        return self._c.get("/users/me/packets", params={"offset": offset, "limit": limit})

    def buy_packet(self, category_id: int, payment_method: str, size: int, packet_type: str = "base") -> dict[str, Any]:
        """Buy a promotion packet."""
        return self._c.post("/users/me/packets", json={
            "category_id": category_id,
            "payment_method": payment_method,
            "size": size,
            "type": packet_type,
        })

    def business_profile(self) -> dict[str, Any]:
        """Get business user profile."""
        return self._c.get("/users-business/me")

    def update_business_profile(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Update business user profile."""
        return self._c.put("/users-business/me", json=payload)
