from app.bot import index_documents, ask

if __name__ == "__main__":
    index_documents()

    questions = [
        "How much storage do I get on the Pro plan?",
        "Can I get a refund on my monthly subscription?",
        "Does the bot support carrier pigeon delivery?",  # trick question, not in context
    ]

    for q in questions:
        print(f"Q: {q}")
        print(f"A: {ask(q)}\n")