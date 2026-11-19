"""Single-conversation Claude CLI demo with injectable API access."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from .storage import connect, recent, save_turn, search


def ask(connection, client, question, model, context_chars=12000):
    """Persist a complete turn only after a valid text response.

    The character budget bounds outbound text approximately; it is not a token
    counter. SDK/API exceptions propagate to the CLI without persisting a turn.
    """
    question = question.strip()
    if not question or len(question) > 8000:
        raise ValueError("Question must contain 1–8000 characters")
    if context_chars < len(question):
        raise ValueError("Question exceeds context budget")
    messages = recent(connection, limit=20)
    while messages and (
        messages[0]["role"] != "user"
        or sum(len(m["content"]) for m in messages) + len(question) > context_chars
    ):
        messages.pop(0)
    messages.append({"role": "user", "content": question})
    response = client.messages.create(
        model=model,
        max_tokens=500,
        system="You are a helpful assistant. Do not claim access to private company systems.",
        messages=messages,
    )
    answer = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()
    if not answer:
        raise ValueError("The model returned no text")
    save_turn(connection, question, answer)
    return answer


def main():
    load_dotenv()
    key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL")
    if not key or not model:
        raise SystemExit(
            "Configure ANTHROPIC_API_KEY and an available ANTHROPIC_MODEL in .env"
        )
    connection = connect(os.getenv("CHAT_DB_PATH", "chat_history.db"))
    print("Unified AI Chatbot DEMO: /search term, /history, /quit")
    try:
        with Anthropic(api_key=key) as client:
            while True:
                question = input("You: ").strip()
                if not question:
                    continue
                if question == "/quit":
                    break
                if question == "/history":
                    for message in recent(connection):
                        print(f"{message['role']}: {message['content']}")
                    continue
                if question.startswith("/search "):
                    for role, content in search(connection, question[8:].strip()):
                        print(f"{role}: {content}")
                    continue
                try:
                    print("Assistant:", ask(connection, client, question, model))
                except Exception as exc:
                    # Do not log SDK exception bodies, API keys or private prompts.
                    print(f"Request failed ({type(exc).__name__}); turn not saved")
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
