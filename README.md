
# AI Customer Support Agent
### Artefact | AI Engineer Technical Challenge

A Python-based conversational AI assistant developed for **Empório da Música**, a fictional musical instrument store in Campo Grande, Brazil.

The project demonstrates how a large language model can interact with structured business data and store policies through function calling, while maintaining conversational context and respecting operational limitations.

## 1. Project Overview

The goal is to build an AI customer support agent capable of answering common questions about products, availability, orders, and store policies.

Instead of relying on the language model's internal knowledge for business information, the assistant retrieves data from local sources using Python tools.

The solution focuses on four priorities:

- Accurate answers grounded in available data
- Simple, maintainable Python architecture
- Multi-turn conversation support
- Clear handling of privacy, uncertainty, and unsupported actions

The application runs through a command-line interface.

## 2. Main Features

### Product catalog

Customers can ask about:

- Available musical instruments
- Product categories
- Prices and stock quantities
- Instruments within a specific budget
- Individual products or model names

Product information is retrieved from the provided CSV datasets.

### Store policies

The assistant can answer questions about:

- Business hours and location
- Payment methods
- Returns and exchanges
- Refund policies
- Shipping and delivery
- Product warranties

Responses use a curated, customer-facing policy knowledge base.

### Demonstration order lookup

The assistant supports synthetic order IDs, such as `DEMO-1001`.

It can retrieve:

- Order status
- Order date
- Estimated delivery date, when available

These records are fictional and are not connected to a production order management system.

### Conversation memory

The assistant maintains context within an active chat session, allowing customers to ask follow-up questions without repeating their original requests.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Language model | Gemini 3.5 Flash-Lite |
| LLM integration | Google Gen AI SDK |
| Tool orchestration | Gemini automatic function calling |
| Structured data | CSV |
| Policy knowledge base | Markdown |
| Conversation interface | Command-line interface |
| Development and testing | Google Colab |
| Version control | Git and GitHub |

The project uses Python's standard library for data loading, text normalization, and file handling.

## 4. Architecture

The solution uses a lightweight tool-based architecture.

```text
Customer
   |
   v
Command-Line Interface
   |
   v
Gemini Chat Session
   |
   +---- check_catalog()
   |        |
   |        +---- products.csv
   |        +---- categories.csv
   |
   +---- get_store_policy()
   |        |
   |        +---- store_policies.md
   |
   +---- lookup_demo_order()
            |
            +---- demo_orders.csv
   |
   v
Grounded Customer Response
```

### How it works

1. The customer submits a question.
2. Gemini interprets the request and its conversational context.
3. The model selects an available Python function when business information is needed.
4. The function retrieves information from the corresponding local data source.
5. The result is returned to the model.
6. Gemini generates a response in Brazilian Portuguese.

The model is instructed not to invent business facts or claim to perform unsupported operations.

## 5. Project Structure

```text
artefact-ai-customer-support-agent/
|
|-- src/
|   |-- agent.py
|   |-- catalog.py
|   |-- policies.py
|   |-- orders.py
|
|-- data/
|   |-- products.csv
|   |-- categories.csv
|   |-- store_policies.md
|   |-- demo_orders.csv
|   |-- README.md
|
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
```

### Main modules

**agent.py**

Initializes the Gemini client, registers the available tools, manages the chat session, and handles the command-line interface.

**catalog.py**

Loads product and category data and supports filtering by category, maximum price, and product name. Inactive and out-of-stock products are excluded.

**policies.py**

Retrieves relevant sections from the store policy knowledge base using keyword-based topic matching.

**orders.py**

Retrieves synthetic order information using demonstration identifiers. It rejects identifiers outside the supported demonstration format.

## 6. Installation and Execution

### Prerequisites

- Python installed locally
- Git
- A Gemini API key
- Internet access for Gemini API requests

### Step 1 — Clone the repository

```bash
git clone https://github.com/MariMecucci/artefact-ai-customer-support-agent.git
cd artefact-ai-customer-support-agent
```

### Step 2 — Install dependencies

```bash
python -m pip install -r requirements.txt
```

Using a Python virtual environment is recommended.

### Step 3 — Configure the API key

Create an API key using Google AI Studio:

https://aistudio.google.com/apikey

The `.env.example` file documents the required variable. The application reads `GEMINI_API_KEY` from the process environment; it does not automatically load `.env` files.

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key"
```

On macOS or Linux:

```bash
export GEMINI_API_KEY="your_api_key"
```

Never commit a real API key to version control.

### Step 4 — Run the agent

```bash
python src/agent.py
```

The assistant will start an interactive conversation.

Type `sair` to close the session.

## 7. Example Questions

### Product recommendations

"Quais violões vocês têm por até R$ 1.000?"

### Specific product lookup

"Quanto custa o Takamine GD20? Tem em estoque?"

### Store policies

"Posso devolver uma compra feita pela internet?"

### Follow-up question

"E quem paga o frete dessa devolução?"

### Demonstration order status

"Qual é o status do pedido DEMO-1001?"

The assistant is expected to retrieve relevant information using its tools before responding.

## 8. Design Decisions

### Why function calling?

Function calling allows the model to request information from explicit Python functions rather than generating unsupported business facts.

This approach separates natural-language interpretation from structured data retrieval.

### Why local CSV files?

The challenge provides structured datasets, making CSV-based access sufficient for a small prototype.

A production implementation would typically use databases or authenticated service APIs.

### Why keyword-based policy retrieval?

The policy knowledge base is relatively small and organized by topic.

A deterministic retrieval approach keeps the prototype lightweight, inexpensive, and easy to inspect.

A semantic retrieval approach could improve coverage for more complex or ambiguous questions.

### Why a command-line interface?

The CLI keeps the project focused on the agent's logic, tool integration, and reliability rather than frontend development.

A web interface can be added without replacing the underlying data access functions.

## 9. Testing and Validation

Development and manual validation were performed using Google Colab.

The following scenarios were exercised successfully:

| Scenario | Observed result |
|---|---|
| Acoustic guitars under R$ 1,000 | 12 matching products |
| Takamine GD20 lookup | R$ 2,199 and 5 units in stock |
| Online return question | Correct policy conditions |
| Follow-up on return shipping | Conversation context preserved |
| DEMO-1001 lookup | Synthetic shipped order identified |
| Unknown demonstration order | Not-found response |
| Real order identifier | Production access limitation explained |
| Unknown product | No invented price |
| Reservation request | Unsupported action declined |
| Unrelated question | Redirected to store-related topics |

These are manual functional checks, not a complete automated test suite.

Model-generated answers may vary between executions.

## 10. Safety and Privacy

The project follows several basic safeguards:

- API keys are obtained through environment variables.
- Real customer records are not published in the repository.
- Demonstration orders use synthetic identifiers and data.
- The model is instructed to avoid unsupported business claims.
- Real order status requires authentication and production integration.
- Reservations, refunds, purchases, and order changes are not implemented.
- Unknown information should be acknowledged rather than invented.

These controls are appropriate for a technical prototype but do not replace production security controls.

## 11. Current Limitations

The current implementation has several known limitations:

- Order data is synthetic and does not reflect real-time production records.
- Policy retrieval uses keyword matching and may struggle with ambiguous or multi-topic questions.
- Category normalization covers common terms but is not exhaustive.
- Conversations are maintained in memory only during the active session.
- No persistent session storage or user authentication is implemented.
- The command-line interface is not a deployed customer-facing application.
- No automated regression test suite is currently included.
- LLM output quality depends on model behavior and API availability.

Future improvements could include authenticated order APIs, a more robust retrieval strategy, automated evaluations, observability, and a web interface.

## 12. Use of AI During Development

ChatGPT was used as a development assistant for architecture planning, Python implementation, debugging, documentation, and test-case design.

Google Gemini is the language model used by the running application.

The project was developed iteratively, with code committed to GitHub and functionality tested through Google Colab.

AI-assisted suggestions were reviewed and adjusted based on observed execution results.

## 13. Conclusion

This project demonstrates a functional conversational AI prototype that combines a language model with business data through Python function calling.

The main engineering objective is to provide useful, context-aware customer support while keeping factual data retrieval separate from language generation and communicating system limitations clearly.

The architecture is intentionally lightweight and provides a foundation for future production-oriented improvements.
