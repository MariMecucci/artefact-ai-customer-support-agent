
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
Use a friendly, professional and concise tone.

You have two tools:

1. check_catalog:
Use it for product prices, categories and stock availability.
Never invent product names, prices or stock quantities.

2. get_store_policy:
Use it for opening hours, store address, payments, returns,
exchanges, refunds, delivery and warranties.
Pass the customer's question as the topic argument.
Never invent store policies.

Always consult the appropriate tool before answering
questions about products or store policies.

Base factual answers only on information returned by tools.

If information is unavailable, explain the limitation
and recommend contacting a human attendant.

Do not pretend to check order status or access customer
records because those capabilities are not implemented yet.

Do not claim to complete reservations, refunds, purchases,
order changes or any other transaction.

Politely redirect questions unrelated to the store.
"""


def ask_agent(question: str) -> str:
    """Answer a customer question using Gemini and available tools."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is missing."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                check_catalog,
                get_store_policy
            ],
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )

    return response.text or (
        "Desculpe, não consegui gerar uma resposta."
    )


def main():
    """Run the command-line customer support agent."""
    print("Empório da Música | AI Customer Support")
    print("Digite 'sair' para encerrar.\n")

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
            answer = ask_agent(question)
            print(f"\nAssistente: {answer}\n")

        except Exception as error:
            print(
                f"\nErro: {type(error).__name__}. "
                "Verifique a configuração e tente novamente.\n"
            )


if __name__ == "__main__":
    main()
