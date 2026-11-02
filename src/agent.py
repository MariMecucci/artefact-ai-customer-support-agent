
import os
import unicodedata

from google import genai
from google.genai import types

from catalog import search_products
from policies import get_store_policy
from orders import lookup_demo_order


MODEL_NAME = "gemini-3.5-flash-lite"


def normalize_category(category: str) -> str:
    """Normalize customer terms to catalog categories."""
    key = unicodedata.normalize(
        "NFKD", category.strip().lower()
    ).encode("ascii", "ignore").decode("utf-8")

    mapping = {
        "violao": "Violões",
        "violoes": "Violões",
        "acoustic guitar": "Violões",
        "acoustic guitars": "Violões",
        "guitarra": "Guitarras",
        "guitarras": "Guitarras",
        "guitar": "Guitarras",
        "guitars": "Guitarras",
    }

    return mapping.get(key, category)


def check_catalog(
    category: str,
    max_price: float = 1000000.0
) -> dict:
    """Find available instruments by category and maximum price in BRL."""
    normalized_category = normalize_category(category)

    products = search_products(
        category=normalized_category,
        max_price=max_price
    )

    return {
        "category": normalized_category,
        "total_found": len(products),
        "products": products
    }


SYSTEM_PROMPT = """
You are the AI customer support assistant for Empório da Música,
a musical instrument store in Campo Grande, Brazil.

Always respond in Brazilian Portuguese.
Be friendly, professional and concise.

You have three tools:

1. check_catalog
Use for product prices, categories and stock availability.

2. get_store_policy
Use for opening hours, address, payment methods,
returns, refunds, exchanges, delivery and warranties.
Pass the customer's question as the topic argument.

3. lookup_demo_order
Use only for synthetic demonstration order status inquiries.
Pass the requested order ID as the order_id argument.

IMPORTANT:
All DEMO-xxxx orders are fictional examples.
Never present demonstration orders as real customer orders.
Never claim the order status is updated in real time.
For real orders, explain that authentication and access
to the store's production system would be required.

Always consult the relevant tool before providing facts.
Never invent products, prices, stock, orders or policies.

Maintain conversation context between messages.
Consult tools again when new information is needed.

If information is unavailable, explain the limitation
and suggest contacting a human attendant.

Never disclose customer personal information.
Never claim to complete purchases, reservations,
refunds, order changes or deliveries.
Do not offer to initiate actions that are not implemented.

Politely redirect questions unrelated to the store.
"""


def create_chat(client):
    """Create a chat with tools and session history."""
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            tools=[
                check_catalog,
                get_store_policy,
                lookup_demo_order
            ],
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )


def main():
    """Run the customer support command-line interface."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY is not configured.")
        return

    print("Empório da Música | AI Customer Support")
    print("Digite 'sair' para encerrar.\n")

    try:
        # Keep the Gemini client open during the conversation.
        with genai.Client(api_key=api_key) as client:
            chat = create_chat(client)

            while True:
                try:
                    question = input("Você: ").strip()

                except (EOFError, KeyboardInterrupt):
                    print("\nAtendimento encerrado.")
                    break

                if question.lower() in {"sair", "exit", "quit"}:
                    print("Atendimento encerrado.")
                    break

                if not question:
                    continue

                try:
                    response = chat.send_message(question)

                    answer = response.text or (
                        "Desculpe, não consegui responder."
                    )

                    print(f"\nAssistente: {answer}\n")

                except Exception as error:
                    print(
                        f"\nErro: {type(error).__name__}. "
                        "Tente novamente ou contate um atendente.\n"
                    )

    except Exception as error:
        print(
            f"Could not initialize Gemini: "
            f"{type(error).__name__}"
        )


if __name__ == "__main__":
    main()
