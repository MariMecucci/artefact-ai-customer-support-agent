
import csv
import re
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "demo_orders.csv"
)


STATUS_LABELS = {
    "shipped": "Pedido enviado",
    "delivered": "Pedido entregue",
    "confirmed": "Pedido confirmado",
    "cancelled": "Pedido cancelado",
}


def lookup_demo_order(order_id: str) -> dict:
    """Look up a synthetic order by its demonstration ID."""

    normalized_id = order_id.strip().upper()

    # Only synthetic demonstration IDs are accepted.
    if not re.fullmatch(r"DEMO-\d{4}", normalized_id):
        return {
            "found": False,
            "demo_only": True,
            "message": (
                "Only synthetic DEMO-xxxx order IDs "
                "are supported. Real orders require "
                "customer identity verification."
            ),
        }

    with DATA_FILE.open(
        encoding="utf-8-sig",
        newline=""
    ) as file:
        orders = csv.DictReader(file)

        for order in orders:
            if order["order_id"] == normalized_id:
                return {
                    "found": True,
                    "demo_only": True,
                    "order_id": normalized_id,
                    "status": order["status"],
                    "status_label": STATUS_LABELS.get(
                        order["status"],
                        "Status desconhecido"
                    ),
                    "order_date": order["order_date"],
                    "estimated_delivery": (
                        order["estimated_delivery"] or None
                    ),
                    "note": (
                        "Synthetic demonstration data. "
                        "Not a real-time order status."
                    ),
                }

    return {
        "found": False,
        "demo_only": True,
        "order_id": normalized_id,
        "message": (
            "No matching demonstration order was found."
        ),
    }


if __name__ == "__main__":
    for order_id in [
        "DEMO-1001",
        "DEMO-1002",
        "DEMO-9999",
        "REAL-1234",
    ]:
        print(f"\nSearching for: {order_id}")
        print(lookup_demo_order(order_id))
