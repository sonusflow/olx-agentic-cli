"""Location endpoints (cities & districts) for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any, Optional

from olx_api.client import OLXClient


class Locations:
    """Browse OLX locations: regions, cities, and districts."""

    def __init__(self, client: OLXClient):
        self._c = client

    def list_regions(self) -> dict[str, Any]:
        """List all regions (voivodeships).

        Returns:
            Parsed JSON with region list.
        """
        return self._c.get("/regions")

    def list_cities(self, region_id: Optional[int] = None) -> dict[str, Any]:
        """List cities, optionally filtered by region.

        Args:
            region_id: Optional region filter.

        Returns:
            Parsed JSON with city list.
        """
        params: dict[str, Any] = {}
        if region_id is not None:
            params["region_id"] = region_id
        return self._c.get("/cities", params=params)

    def get_city(self, city_id: int) -> dict[str, Any]:
        """Get city details.

        Args:
            city_id: The numeric city ID.

        Returns:
            Parsed JSON with city info.
        """
        return self._c.get(f"/cities/{city_id}")

    def list_districts(self, city_id: int) -> dict[str, Any]:
        """List districts of a city.

        Args:
            city_id: The numeric city ID.

        Returns:
            Parsed JSON with district list.
        """
        return self._c.get(f"/cities/{city_id}/districts")

    def reverse_geocode(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Find city/district from coordinates."""
        return self._c.get("/locations", params={"latitude": latitude, "longitude": longitude})
