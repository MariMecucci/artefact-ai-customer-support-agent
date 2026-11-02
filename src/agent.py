
import os
import unicodedata

from google import genai
from google.genai import types

from catalog import search_products
from policies import get_store_policy


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

Use check_catalog for prices, products and stock.
Use get_store_policy for opening hours, address, payment,
returns, exchanges, delivery and warranties.

Always consult the appropriate tool before giving factual answers.
Use the customer's question when searching store policies.
Never invent prices, stock quantities or store policies.

Keep track of the conversation context.
Understand follow-up questions using previous messages.
Consult the appropriate tool again when new facts are needed.

If information is unavailable, explain the limitation
and suggest contacting a human attendant.

Do not access or disclose customer records.
Order status lookup is not implemented yet.

Never claim to complete purchases, reservations,
refunds, order changes or deliveries.

Politely redirect questions unrelated to the store.
"""


def create_chat(client):
    """Create a chat using an active Gemini client."""
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            tools=[check_catalog, get_store_policy],
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )


def main():
    """Run a customer support chat with a managed client."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY is not configured.")
        return

    print("Empório da Música | AI Customer Support")
    print("Digite 'sair' para encerrar.\n")

    try:
        # Keep the Gemini client open throughout the conversation.
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
