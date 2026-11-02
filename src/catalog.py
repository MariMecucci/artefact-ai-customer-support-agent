
import csv
import unicodedata
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename):
    """Load records from a CSV file."""
    with (DATA_DIR / filename).open(
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return list(csv.DictReader(file))


def normalize_text(value):
    """Normalize text for accent-insensitive searches."""
    return unicodedata.normalize(
        "NFKD", value.strip().casefold()
    ).encode("ascii", "ignore").decode("utf-8")


def search_products(
    category=None,
    max_price=None,
    product_name=None
):
    """Search active, in-stock products using optional filters."""
    products = load_csv("products.csv")

    categories = {
        row["category_id"]: row["name"]
        for row in load_csv("categories.csv")
    }

    results = []

    for product in products:
        if product["status"].lower() != "active":
            continue

        stock = int(product["stock_quantity"])

        if stock <= 0:
            continue

        category_name = categories.get(
            product["category_id"], "Unknown"
        )

        price = float(product["price_brl"])
        name = product["name"]

        if category:
            if normalize_text(category) not in normalize_text(category_name):
                continue

        if max_price is not None and price > max_price:
            continue

        if product_name:
            if normalize_text(product_name) not in normalize_text(name):
                continue

        results.append({
            "name": name,
            "category": category_name,
            "price_brl": price,
            "stock_quantity": stock
        })

    return sorted(
        results,
        key=lambda item: item["price_brl"]
    )


if __name__ == "__main__":
    # Test 1: Category and price filters
    affordable = search_products(
        category="Violões",
        max_price=1000
    )

    print(f"Affordable acoustic guitars: {len(affordable)}")

    # Test 2: Specific product lookup
    takamine = search_products(
        product_name="Takamine GD20"
    )

    print("\nSpecific product search:")

    for product in takamine:
        print(
            f"{product['name']} | "
            f"R$ {product['price_brl']:.2f} | "
            f"Stock: {product['stock_quantity']}"
        )
