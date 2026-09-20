from datetime import date
from typing import Optional

from fastmcp import FastMCP


mcp = FastMCP(name="Hotel MCP Server")


# ------------------------------------------------------------------
# Mock database
# ------------------------------------------------------------------

HOTELS = [
    {
        "hotel_id": "H001",
        "name": "Taj Resort Goa",
        "city": "Goa",
        "country": "India",
        "rating": 5,
        "price_per_night": 18000,
        "currency": "INR",
        "amenities": [
            "pool",
            "wifi",
            "spa",
            "restaurant",
            "beach_access",
        ],
    },
    {
        "hotel_id": "H002",
        "name": "Goa Marriott Resort",
        "city": "Goa",
        "country": "India",
        "rating": 5,
        "price_per_night": 15000,
        "currency": "INR",
        "amenities": [
            "pool",
            "wifi",
            "spa",
            "restaurant",
        ],
    },
    {
        "hotel_id": "H003",
        "name": "The Leela Palace Bengaluru",
        "city": "Bengaluru",
        "country": "India",
        "rating": 5,
        "price_per_night": 14000,
        "currency": "INR",
        "amenities": [
            "pool",
            "wifi",
            "gym",
            "restaurant",
            "spa",
        ],
    },
    {
        "hotel_id": "H004",
        "name": "ITC Gardenia",
        "city": "Bengaluru",
        "country": "India",
        "rating": 5,
        "price_per_night": 12000,
        "currency": "INR",
        "amenities": [
            "pool",
            "wifi",
            "gym",
            "restaurant",
        ],
    },
]


# ------------------------------------------------------------------
# MCP Tools
# ------------------------------------------------------------------

@mcp.tool
def search_hotels(
    city: str,
    check_in: Optional[str] = None,
    check_out: Optional[str] = None,
    guests: int = 2,
    max_price: Optional[int] = None,
    min_rating: Optional[int] = None,
) -> list[dict]:
    """
    Search hotels by city and optional price/rating filters.

    Args:
        city: City where the hotel should be located.
        check_in: Check-in date in YYYY-MM-DD format.
        check_out: Check-out date in YYYY-MM-DD format.
        guests: Number of guests.
        max_price: Maximum price per night in local currency.
        min_rating: Minimum hotel rating.
    """

    results = []

    for hotel in HOTELS:
        if hotel["city"].lower() != city.lower():
            continue

        if max_price is not None:
            if hotel["price_per_night"] > max_price:
                continue

        if min_rating is not None:
            if hotel["rating"] < min_rating:
                continue

        results.append(hotel)

    return results


@mcp.tool
def get_hotel_details(hotel_id: str) -> dict:
    """
    Get complete details for a hotel.

    Args:
        hotel_id: Unique hotel identifier.
    """

    for hotel in HOTELS:
        if hotel["hotel_id"] == hotel_id:
            return hotel

    return {
        "error": f"Hotel {hotel_id} was not found."
    }


@mcp.tool
def check_availability(hotel_id: str, check_in: str, check_out: str, guests: int) -> dict:
    """
    Check whether a hotel has rooms available.

    Args:
        hotel_id: Unique hotel identifier.
        check_in: Check-in date YYYY-MM-DD.
        check_out: Check-out date YYYY-MM-DD.
        guests: Number of guests.
    """

    hotel = next(
        (
            hotel
            for hotel in HOTELS
            if hotel["hotel_id"] == hotel_id
        ),
        None,
    )

    if not hotel:
        return {
            "available": False,
            "error": "Hotel not found",
        }

    return {
        "available": True,
        "hotel_id": hotel_id,
        "hotel_name": hotel["name"],
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "rooms_available": 5,
        "price_per_night": hotel["price_per_night"],
        "currency": hotel["currency"],
    }


@mcp.tool
def create_booking(hotel_id: str, check_in: str, check_out: str, guests: int, guest_name: str) -> dict:
    """
    Create a hotel booking.

    IMPORTANT:
    This is a write operation and should only be executed when
    the user explicitly asks to make a booking.

    Args:
        hotel_id: Hotel ID.
        check_in: Check-in date.
        check_out: Check-out date.
        guests: Number of guests.
        guest_name: Guest's full name.
    """

    hotel = next(
        (
            hotel
            for hotel in HOTELS
            if hotel["hotel_id"] == hotel_id
        ),
        None,
    )

    if not hotel:
        return {
            "success": False,
            "error": "Hotel not found",
        }

    return {
        "success": True,
        "booking_id": "BK-2026-000001",
        "hotel_id": hotel_id,
        "hotel_name": hotel["name"],
        "guest_name": guest_name,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "status": "confirmed",
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8001,
    )
