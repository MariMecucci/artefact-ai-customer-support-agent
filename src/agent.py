
import os
import unicodedata

from google import genai
from google.genai import types

from catalog import search_products
from policies import get_store_policy
from orders import lookup_demo_order


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MODEL_NAME = "gemini-3.5-flash-lite"


# --------------------------------------------------
# Product category normalization
# --------------------------------------------------

def normalize_category(category: str) -> str:
    """Normalize customer terms to catalog categories."""

    key = unicodedata.normalize(
        "NFKD",
        category.strip().lower()
    ).encode("ascii", "ignore").decode("utf-8")

    category_mapping = {
        "violao": "Violões",
        "violoes": "Violões",
        "acoustic guitar": "Violões",
        "acoustic guitars": "Violões",
        "guitarra": "Guitarras",
        "guitarras": "Guitarras",
        "guitar": "Guitarras",
        "guitars": "Guitarras",
    }

    return category_mapping.get(key, category)


# --------------------------------------------------
# Tool 1: Product catalog
# --------------------------------------------------

def check_catalog(
    category: str = "",
    max_price: float = 1000000.0,
    product_name: str = ""
) -> dict:
    """
    Search available instruments by category,
    specific model name, or maximum price in BRL.
    """

    normalized_category = (
        normalize_category(category)
        if category else None
    )

    products = search_products(
        category=normalized_category,
        max_price=max_price,
        product_name=product_name or None
    )

    return {
        "category": normalized_category,
        "product_name": product_name or None,
        "total_found": len(products),
        "products": products
    }


# --------------------------------------------------
# AI agent instructions
# --------------------------------------------------

SYSTEM_PROMPT = """
You are the AI customer support assistant for Empório da Música,
a musical instrument store in Campo Grande, Brazil.

PERSONA:
- Always respond in Brazilian Portuguese.
- Be friendly, professional, helpful and concise.
- Use natural language suitable for customer support.

AVAILABLE TOOLS:

1. check_catalog
Use this tool for:
- Product prices
- Product availability and stock
- Instrument categories
- Specific product names and models
- Products within a customer's budget

For specific model questions, use the product_name parameter.
For category searches, use the category parameter.
Use max_price when the customer specifies a budget.

Examples:
- "Quais violões custam até R$ 1000?"
- "Quanto custa o Takamine GD20?"
- "Vocês têm Yamaha C40 disponível?"

Never invent products, prices or stock quantities.

2. get_store_policy
Use this tool for:
- Opening hours
- Store address
- Payment methods
- Returns and exchanges
- Refund policies
- Delivery and shipping
- Product warranties

Pass the customer's question as the topic argument.
Only provide information supported by the returned policy.

3. lookup_demo_order
Use this tool for synthetic order status inquiries.

IMPORTANT:
All DEMO-xxxx orders are fictional demonstration records.

Never present demonstration orders as real customer orders.
Never claim that demonstration data is updated in real time.

For real orders, explain that customer authentication
and access to the production system would be required.

SAFETY AND RELIABILITY:

- Always consult the relevant tool before providing factual
  information about products, store policies or orders.
- Never invent prices, inventory, policies, orders or delivery dates.
- Never disclose customer personal information.
- Never claim to complete purchases, reservations,
  refunds, order changes or deliveries.
- Do not offer to perform actions that are not implemented.
- If information is unavailable, explain the limitation
  and recommend contacting a human attendant.

CONVERSATION:

- Maintain context between messages during the session.
- Understand follow-up questions using previous messages.
- Consult the relevant tool again when new facts are required.
- Avoid repeating information unnecessarily.

OUT-OF-SCOPE QUESTIONS:

If the customer asks something unrelated to the store,
politely explain that you assist with musical instruments,
orders and store policies.
"""


# --------------------------------------------------
# Gemini chat initialization
# --------------------------------------------------

def create_chat(client):
    """
    Create a Gemini chat session with
    automatic function calling and conversation history.
    """

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


# --------------------------------------------------
# Command-line interface
# --------------------------------------------------

def main():
    """Run the customer support agent."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY is not configured."
        )
        return

    print("=" * 50)
    print("Empório da Música | AI Customer Support")
    print("=" * 50)
    print("Olá! Como posso ajudar?")
    print("Digite 'sair' para encerrar.\n")

    try:
        # Keep the client open during the entire session.
        with genai.Client(api_key=api_key) as client:

            chat = create_chat(client)

            while True:

                try:
                    question = input("Você: ").strip()

                except (EOFError, KeyboardInterrupt):
                    print("\nAtendimento encerrado.")
                    break

                # Exit commands
                if question.lower() in {
                    "sair",
                    "exit",
                    "quit"
                }:
                    print("Atendimento encerrado.")
                    break

                if not question:
                    continue

                try:
                    # Gemini automatically selects the relevant tool.
                    response = chat.send_message(question)

                    answer = response.text or (
                        "Desculpe, não consegui responder "
                        "à sua solicitação."
                    )

                    print(f"\nAssistente: {answer}\n")

                except Exception as error:
                    print(
                        f"\nErro: {type(error).__name__}. "
                        "Não foi possível processar "
                        "sua solicitação. Tente novamente.\n"
                    )

    except Exception as error:
        print(
            f"Could not initialize Gemini: "
            f"{type(error).__name__}"
        )


if __name__ == "__main__":
    main()
