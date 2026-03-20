"""Threads & messages for OLX Partner API v2.0."""

from __future__ import annotations

from typing import Any, Optional

from olx_api.client import OLXClient


class Messages:
    """Manage OLX message threads and individual messages."""

    def __init__(self, client: OLXClient):
        self._c = client

    def list_threads(
        self,
        offset: int = 0,
        limit: int = 10,
        advert_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """List message threads for the authenticated user.

        Args:
            offset: Pagination offset.
            limit: Results per page.
            advert_id: Optional filter by advert.

        Returns:
            Parsed JSON with thread list.
        """
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if advert_id is not None:
            params["advert_id"] = advert_id
        return self._c.get("/threads", params=params)

    def get_thread(self, thread_id: int) -> dict[str, Any]:
        """Get a single thread's metadata.

        Args:
            thread_id: The numeric thread ID.

        Returns:
            Parsed JSON with thread details.
        """
        return self._c.get(f"/threads/{thread_id}")

    def list_messages(
        self,
        thread_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> dict[str, Any]:
        """List messages inside a thread.

        Args:
            thread_id: The numeric thread ID.
            offset: Pagination offset.
            limit: Results per page.

        Returns:
            Parsed JSON with messages list.
        """
        return self._c.get(
            f"/threads/{thread_id}/messages",
            params={"offset": offset, "limit": limit},
        )

    def send(self, thread_id: int, text: str) -> dict[str, Any]:
        """Send a message to a thread.

        Args:
            thread_id: The numeric thread ID.
            text: Message body.

        Returns:
            Parsed JSON with the sent message.
        """
        return self._c.post(
            f"/threads/{thread_id}/messages",
            json={"text": text},
        )

    def mark_read(self, thread_id: int) -> None:
        """Mark all messages in a thread as read.

        Args:
            thread_id: The numeric thread ID.
        """
        self._c.post(f"/threads/{thread_id}/commands", json={"command": "mark-as-read"})

    def set_favourite(self, thread_id: int, favourite: bool = True) -> None:
        """Toggle the favourite flag on a thread.

        Args:
            thread_id: The numeric thread ID.
            favourite: True to mark as favourite, False to unmark.
        """
        cmd = "set-favourite" if favourite else "unset-favourite"
        self._c.post(f"/threads/{thread_id}/commands", json={"command": cmd})
