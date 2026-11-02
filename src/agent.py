
import os
import unicodedata

from google import genai
from google.genai import types

from catalog import search_products


MODEL_NAME = "gemini-3.5-flash-lite"


def normalize_category(category: str) -> str:
    """Normalize common customer terms to catalog categories."""
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
You are the customer support assistant for Empório da Música,
a musical instrument store in Campo Grande, Brazil.

Always reply in Brazilian Portuguese.
Be friendly, professional and concise.

For prices and availability, always use check_catalog.
Use 'Violões' for acoustic guitars and 'Guitarras'
for electric guitars.

Only provide prices and stock confirmed by the tool.
Never invent products, prices, inventory or store policies.
When information is unavailable, say so clearly.

When listing the cheapest products, sort by price.
"""


def ask_agent(question: str) -> str:
    """Generate a response using Gemini and the catalog tool."""
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
            tools=[check_catalog],
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1
        )
    )

    return response.text or (
        "Desculpe, não consegui gerar uma resposta."
    )


def main():
    """Run a simple command-line customer support interface."""
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
                "Verifique a configuração da API.\n"
            )


if __name__ == "__main__":
    main()
