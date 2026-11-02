
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename):
    with (DATA_DIR / filename).open(
        encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


def search_products(category=None, max_price=None):
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

        if category and category.casefold() not in category_name.casefold():
            continue

        if max_price is not None and price > max_price:
            continue

        results.append({
            "name": product["name"],
            "category": category_name,
            "price_brl": price,
            "stock_quantity": stock
        })

    return sorted(results, key=lambda item: item["price_brl"])


if __name__ == "__main__":
    products = search_products(category="Violões", max_price=1000)

    print(f"Available guitars under R$ 1,000: {len(products)}")

    for product in products:
        print(
            f"{product['name']} | "
            f"R$ {product['price_brl']:.2f} | "
            f"Stock: {product['stock_quantity']}"
        )
