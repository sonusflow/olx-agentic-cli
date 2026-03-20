#!/usr/bin/env python3
"""OLX CLI — command-line interface for the OLX Partner API v2.0.

Author: sonusflow (https://github.com/sonusflow)
License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from config import load_config, save_config, load_tokens, DEFAULT_REDIRECT_URI
from olx_api.auth import TokenManager, AuthError
from olx_api.client import OLXClient, OLXAPIError


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _pretty(data: object) -> None:
    """Print JSON data with indentation."""
    click.echo(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _get_client() -> OLXClient:
    """Instantiate an authenticated OLXClient."""
    tm = TokenManager()
    return OLXClient(tm)


def _load_json_payload(json_file: Optional[str], prompt: str = "Paste JSON (Ctrl-D when done):") -> dict:
    """Load a JSON payload from a file path or stdin."""
    if json_file:
        return json.loads(Path(json_file).read_text(encoding="utf-8"))
    click.echo(prompt)
    return json.loads(sys.stdin.read())


# ------------------------------------------------------------------
# Root group
# ------------------------------------------------------------------

@click.group()
@click.version_option("2.0.0", prog_name="olx-agentic-cli")
def cli() -> None:
    """OLX CLI — manage your OLX.pl marketplace from the terminal."""
    pass


# ------------------------------------------------------------------
# Setup / Auth commands
# ------------------------------------------------------------------

@cli.command()
def setup() -> None:
    """Configure OLX API credentials and redirect URI."""
    click.echo("OLX API Setup")
    click.echo("=" * 40)
    click.echo("You need a Partner API application from https://developer.olx.pl\n")

    client_id = click.prompt("Client ID")
    client_secret = click.prompt("Client Secret", hide_input=True)
    redirect_uri = click.prompt(
        "Redirect URI",
        default=DEFAULT_REDIRECT_URI,
        show_default=True,
    )

    save_config({
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    })
    click.echo("\nCredentials saved to ~/.olx-integration/config.json")


@cli.command()
@click.option("--local", is_flag=True, help="Use local callback server (dev mode).")
def login(local: bool) -> None:
    """Authenticate with OLX via OAuth 2.0."""
    try:
        tm = TokenManager()
        tm.authorize_interactive(local=local)
        click.echo("Login successful! Tokens saved.")
    except AuthError as exc:
        click.echo(f"Login failed: {exc}", err=True)
        raise SystemExit(1)


@cli.command()
def logout() -> None:
    """Clear stored OAuth tokens."""
    tm = TokenManager()
    tm.logout()
    click.echo("Logged out — tokens removed.")


@cli.command()
def status() -> None:
    """Show authentication status."""
    cfg = load_config()
    tokens = load_tokens()

    click.echo("OLX CLI Status")
    click.echo("=" * 40)

    has_creds = bool(cfg.get("client_id") and cfg.get("client_secret"))
    click.echo(f"Credentials configured: {'yes' if has_creds else 'no'}")
    click.echo(f"Redirect URI:           {cfg.get('redirect_uri', DEFAULT_REDIRECT_URI)}")

    if not tokens.get("access_token"):
        click.echo("Authenticated:          no")
        return

    click.echo("Authenticated:          yes")
    expires_at = tokens.get("expires_at", 0)
    exp_dt = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    now = time.time()
    remaining = int(expires_at - now)

    if remaining > 0:
        click.echo(f"Token expires:          {exp_dt:%Y-%m-%d %H:%M:%S %Z}")
        click.echo(f"Time remaining:         {remaining // 60}m {remaining % 60}s")
    else:
        click.echo("Token status:           EXPIRED (will auto-refresh on next request)")


# ------------------------------------------------------------------
# Adverts
# ------------------------------------------------------------------

@cli.group()
def adverts() -> None:
    """Manage adverts (listings)."""
    pass


@adverts.command("list")
@click.option("--offset", default=0, help="Pagination offset.")
@click.option("--limit", default=10, help="Results per page (max 50).")
def adverts_list(offset: int, limit: int) -> None:
    """List your adverts."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).list(offset=offset, limit=limit))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("get")
@click.argument("advert_id", type=int)
def adverts_get(advert_id: int) -> None:
    """Get details for a single advert."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).get(advert_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("create")
@click.option("--file", "json_file", type=click.Path(exists=True), help="JSON file with advert payload.")
def adverts_create(json_file: Optional[str]) -> None:
    """Create a new advert from a JSON file or stdin."""
    try:
        from olx_api.adverts import Adverts
        payload = _load_json_payload(json_file, "Paste advert JSON (Ctrl-D when done):")
        client = _get_client()
        _pretty(Adverts(client).create(payload))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        click.echo(f"Invalid JSON: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("update")
@click.argument("advert_id", type=int)
@click.option("--file", "json_file", type=click.Path(exists=True), help="JSON file with update payload.")
def adverts_update(advert_id: int, json_file: Optional[str]) -> None:
    """Update an existing advert from a JSON file or stdin."""
    try:
        from olx_api.adverts import Adverts
        payload = _load_json_payload(json_file, "Paste update JSON (Ctrl-D when done):")
        client = _get_client()
        _pretty(Adverts(client).update(advert_id, payload))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        click.echo(f"Invalid JSON: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("delete")
@click.argument("advert_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this advert?")
def adverts_delete(advert_id: int) -> None:
    """Delete (deactivate) an advert."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        Adverts(client).delete(advert_id)
        click.echo(f"Advert {advert_id} deleted.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("activate")
@click.argument("advert_id", type=int)
def adverts_activate(advert_id: int) -> None:
    """Activate a draft or deactivated advert."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).activate(advert_id))
        click.echo(f"Advert {advert_id} activated.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("deactivate")
@click.argument("advert_id", type=int)
def adverts_deactivate(advert_id: int) -> None:
    """Deactivate an active advert."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).deactivate(advert_id))
        click.echo(f"Advert {advert_id} deactivated.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("finish")
@click.argument("advert_id", type=int)
def adverts_finish(advert_id: int) -> None:
    """Mark an advert as finished (sold)."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        Adverts(client).finish(advert_id)
        click.echo(f"Advert {advert_id} marked as finished.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("extend")
@click.argument("advert_id", type=int)
def adverts_extend(advert_id: int) -> None:
    """Extend an advert's validity period."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        Adverts(client).extend(advert_id)
        click.echo(f"Advert {advert_id} extended.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("stats")
@click.argument("advert_id", type=int)
def adverts_stats(advert_id: int) -> None:
    """Get advert statistics (views, phone views, observers)."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).statistics(advert_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@adverts.command("moderation-reason")
@click.argument("advert_id", type=int)
def adverts_moderation(advert_id: int) -> None:
    """Get moderation rejection reason for an advert."""
    try:
        from olx_api.adverts import Adverts
        client = _get_client()
        _pretty(Adverts(client).moderation_reason(advert_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Messages
# ------------------------------------------------------------------

@cli.group()
def messages() -> None:
    """Manage message threads."""
    pass


@messages.command("list")
@click.option("--offset", default=0, help="Pagination offset.")
@click.option("--limit", default=10, help="Results per page.")
def messages_list(offset: int, limit: int) -> None:
    """List message threads."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        _pretty(Messages(client).list_threads(offset=offset, limit=limit))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@messages.command("get")
@click.argument("thread_id", type=int)
def messages_get(thread_id: int) -> None:
    """Get messages in a thread."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        _pretty(Messages(client).list_messages(thread_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@messages.command("thread")
@click.argument("thread_id", type=int)
def messages_thread(thread_id: int) -> None:
    """Get thread metadata."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        _pretty(Messages(client).get_thread(thread_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@messages.command("send")
@click.argument("thread_id", type=int)
@click.argument("text")
def messages_send(thread_id: int, text: str) -> None:
    """Send a message to a thread."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        result = Messages(client).send(thread_id, text)
        click.echo("Message sent.")
        _pretty(result)
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@messages.command("mark-read")
@click.argument("thread_id", type=int)
def messages_mark_read(thread_id: int) -> None:
    """Mark all messages in a thread as read."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        Messages(client).mark_read(thread_id)
        click.echo(f"Thread {thread_id} marked as read.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@messages.command("favourite")
@click.argument("thread_id", type=int)
@click.option("--remove", is_flag=True, help="Remove favourite instead of setting it.")
def messages_favourite(thread_id: int, remove: bool) -> None:
    """Toggle favourite on a thread."""
    try:
        from olx_api.messages import Messages
        client = _get_client()
        Messages(client).set_favourite(thread_id, favourite=not remove)
        action = "removed from" if remove else "added to"
        click.echo(f"Thread {thread_id} {action} favourites.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Categories
# ------------------------------------------------------------------

@cli.group()
def categories() -> None:
    """Browse categories."""
    pass


@categories.command("list")
@click.option("--parent", "parent_id", type=int, default=None, help="Parent category ID.")
def categories_list(parent_id: Optional[int]) -> None:
    """List categories."""
    try:
        from olx_api.categories import Categories
        client = _get_client()
        _pretty(Categories(client).list(parent_id=parent_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@categories.command("get")
@click.argument("category_id", type=int)
def categories_get(category_id: int) -> None:
    """Get details for a single category."""
    try:
        from olx_api.categories import Categories
        client = _get_client()
        _pretty(Categories(client).get(category_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@categories.command("attributes")
@click.argument("category_id", type=int)
def categories_attributes(category_id: int) -> None:
    """Get attributes (fields) required for a category."""
    try:
        from olx_api.categories import Categories
        client = _get_client()
        _pretty(Categories(client).attributes(category_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@categories.command("suggest")
@click.argument("query")
def categories_suggest(query: str) -> None:
    """Search categories by name (min 3 characters)."""
    try:
        from olx_api.categories import Categories
        client = _get_client()
        _pretty(Categories(client).suggest(query))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# User
# ------------------------------------------------------------------

@cli.group()
def user() -> None:
    """User account commands."""
    pass


@user.command("me")
def user_me() -> None:
    """Get current user info."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).me())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("get")
@click.argument("user_id", type=int)
def user_get(user_id: int) -> None:
    """Get a public user profile."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).get(user_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("balance")
def user_balance() -> None:
    """Get account balance."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).account_balance())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("payment-methods")
def user_payment_methods() -> None:
    """List available payment methods."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).payment_methods())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("billing")
@click.option("--page", default=1, help="Page number.")
@click.option("--limit", default=20, help="Results per page.")
def user_billing(page: int, limit: int) -> None:
    """Get billing transaction history."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).billing(page=page, limit=limit))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("invoices")
@click.option("--type", "invoice_type", type=click.Choice(["prepaid", "postpaid"]), default="prepaid", help="Invoice type.")
@click.option("--page", default=1, help="Page number.")
@click.option("--limit", default=20, help="Results per page.")
def user_invoices(invoice_type: str, page: int, limit: int) -> None:
    """Get invoices (prepaid or postpaid)."""
    try:
        from olx_api.users import Users
        client = _get_client()
        users = Users(client)
        if invoice_type == "prepaid":
            _pretty(users.prepaid_invoices(page=page, limit=limit))
        else:
            _pretty(users.postpaid_invoices(page=page, limit=limit))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@user.command("business")
def user_business() -> None:
    """Get business user profile."""
    try:
        from olx_api.users import Users
        client = _get_client()
        _pretty(Users(client).business_profile())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Locations
# ------------------------------------------------------------------

@cli.group()
def locations() -> None:
    """Browse locations (regions, cities, districts)."""
    pass


@locations.command("regions")
def locations_regions() -> None:
    """List all regions (voivodeships)."""
    try:
        from olx_api.locations import Locations
        client = _get_client()
        _pretty(Locations(client).list_regions())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@locations.command("cities")
@click.option("--region", "region_id", type=int, default=None, help="Filter by region ID.")
def locations_cities(region_id: Optional[int]) -> None:
    """List cities, optionally filtered by region."""
    try:
        from olx_api.locations import Locations
        client = _get_client()
        _pretty(Locations(client).list_cities(region_id=region_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@locations.command("get-city")
@click.argument("city_id", type=int)
def locations_get_city(city_id: int) -> None:
    """Get city details."""
    try:
        from olx_api.locations import Locations
        client = _get_client()
        _pretty(Locations(client).get_city(city_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@locations.command("districts")
@click.argument("city_id", type=int)
def locations_districts(city_id: int) -> None:
    """List districts of a city."""
    try:
        from olx_api.locations import Locations
        client = _get_client()
        _pretty(Locations(client).list_districts(city_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@locations.command("geocode")
@click.argument("latitude", type=float)
@click.argument("longitude", type=float)
def locations_geocode(latitude: float, longitude: float) -> None:
    """Find city/district from coordinates."""
    try:
        from olx_api.locations import Locations
        client = _get_client()
        _pretty(Locations(client).reverse_geocode(latitude, longitude))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Payments
# ------------------------------------------------------------------

@cli.group()
def payments() -> None:
    """Payments, paid features, and promotions."""
    pass


@payments.command("features")
@click.argument("advert_id", type=int)
def payments_features(advert_id: int) -> None:
    """List paid features available for an advert."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        _pretty(Payments(client).list_paid_features(advert_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@payments.command("apply-feature")
@click.argument("advert_id", type=int)
@click.argument("feature")
def payments_apply_feature(advert_id: int, feature: str) -> None:
    """Apply a paid feature to an advert (e.g. promote, urgent, top_ad)."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        _pretty(Payments(client).apply_paid_feature(advert_id, feature))
        click.echo(f"Feature '{feature}' applied to advert {advert_id}.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@payments.command("packets")
def payments_packets() -> None:
    """List available promotion packets."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        _pretty(Payments(client).list_packets())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@payments.command("history")
@click.option("--offset", default=0, help="Pagination offset.")
@click.option("--limit", default=20, help="Results per page.")
def payments_history(offset: int, limit: int) -> None:
    """List payment history."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        _pretty(Payments(client).list_payments(offset=offset, limit=limit))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@payments.command("all-features")
def payments_all_features() -> None:
    """List all available paid feature types."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        _pretty(Payments(client).list_all_features())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@payments.command("apply-packet")
@click.argument("advert_id", type=int)
@click.option("--method", default="account", help="Payment method (account/postpaid).")
def payments_apply_packet(advert_id: int, method: str) -> None:
    """Apply a promotion packet to an advert."""
    try:
        from olx_api.payments import Payments
        client = _get_client()
        Payments(client).apply_packet(advert_id, payment_method=method)
        click.echo(f"Packet applied to advert {advert_id}.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Delivery
# ------------------------------------------------------------------

@cli.group()
def delivery() -> None:
    """Delivery methods and shipments."""
    pass


@delivery.command("methods")
def delivery_methods() -> None:
    """List available delivery methods."""
    try:
        from olx_api.delivery import Delivery
        client = _get_client()
        _pretty(Delivery(client).list_methods())
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@delivery.command("get-shipment")
@click.argument("advert_id", type=int)
def delivery_get_shipment(advert_id: int) -> None:
    """Get shipment information for an advert."""
    try:
        from olx_api.delivery import Delivery
        client = _get_client()
        _pretty(Delivery(client).get_shipment(advert_id))
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@delivery.command("create-shipment")
@click.argument("advert_id", type=int)
@click.option("--file", "json_file", type=click.Path(exists=True), help="JSON file with shipment payload.")
def delivery_create_shipment(advert_id: int, json_file: Optional[str]) -> None:
    """Create a shipment for a sold advert."""
    try:
        from olx_api.delivery import Delivery
        payload = _load_json_payload(json_file, "Paste shipment JSON (Ctrl-D when done):")
        client = _get_client()
        _pretty(Delivery(client).create_shipment(advert_id, payload))
        click.echo(f"Shipment created for advert {advert_id}.")
    except (AuthError, OLXAPIError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        click.echo(f"Invalid JSON: {exc}", err=True)
        raise SystemExit(1)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    cli()
