
import re
import unicodedata
from pathlib import Path

POLICY_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "store_policies.md"
)

TOPIC_KEYWORDS = {
    "Delivery": [
        "entrega", "frete", "envio", "transportadora",
        "rastreamento", "delivery", "shipping"
    ],
    "Returns and Exchanges": [
        "devolv", "devolucao", "troca", "arrepend",
        "reembolso", "return", "refund", "exchange"
    ],
    "Warranty": [
        "garantia", "defeito", "conserto", "warranty"
    ],
    "Payment Methods": [
        "pagamento", "pagar", "pix", "cartao",
        "parcelamento", "boleto", "payment"
    ],
    "Store Information": [
        "horario", "funcionamento", "endereco",
        "localizacao", "telefone", "whatsapp",
        "opening hours", "address"
    ],
    "Customer Support Rules": [
        "atendimento", "reclamacao", "suporte",
        "atendente", "support"
    ]
}


def normalize_text(text: str) -> str:
    """Remove accents and standardize text for matching."""
    return unicodedata.normalize(
        "NFKD", text.casefold()
    ).encode("ascii", "ignore").decode("utf-8")


def load_policy_sections() -> dict:
    """Read policy sections from the Markdown knowledge base."""
    content = POLICY_FILE.read_text(encoding="utf-8")

    sections = {}

    for block in re.split(r"(?m)^##\s+", content)[1:]:
        heading, separator, body = block.partition("\n")

        if separator:
            sections[heading.strip()] = body.strip()

    return sections


def get_store_policy(topic: str) -> dict:
    """Retrieve store policies relevant to a customer question."""
    normalized_topic = normalize_text(topic)
    sections = load_policy_sections()

    for heading, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in normalized_topic for keyword in keywords):
            policy_text = sections.get(heading)

            if policy_text:
                return {
                    "found": True,
                    "topic": heading,
                    "source": "data/store_policies.md",
                    "policy_text": policy_text
                }

    return {
        "found": False,
        "topic": topic,
        "message": (
            "No matching store policy was found. "
            "Do not invent a policy. "
            "Suggest contacting a human attendant."
        )
    }


if __name__ == "__main__":
    for question in [
        "Qual o horário de funcionamento?",
        "Posso devolver minha compra?",
        "Como funciona o frete?"
    ]:
        result = get_store_policy(question)

        print(f"\nQuestion: {question}")
        print(f"Found: {result['found']}")
        print(f"Topic: {result['topic']}")
