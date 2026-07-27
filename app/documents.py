"""Sample knowledge base for the RAG bot to answer questions from."""

DOCUMENTS = [
    {
        "id": "doc1",
        "text": "CloudSync Pro offers 500GB of storage on the Basic plan, "
                "priced at $9.99/month. The Pro plan includes 2TB of storage "
                "for $19.99/month."
    },
    {
        "id": "doc2",
        "text": "CloudSync Pro supports automatic backup for Windows, macOS, "
                "and Linux. Mobile apps are available for iOS and Android, "
                "but do not support automatic background backup due to OS "
                "restrictions."
    },
    {
        "id": "doc3",
        "text": "Refunds are available within 14 days of purchase for annual "
                "plans. Monthly plans are non-refundable but can be canceled "
                "at any time without further charges."
    },
    {
        "id": "doc4",
        "text": "CloudSync Pro uses AES-256 encryption for files at rest and "
                "TLS 1.3 for files in transit. Two-factor authentication is "
                "available but not enabled by default."
    },
    {
        "id": "doc5",
        "text": "The maximum single file upload size is 5GB on all plans. "
                "There is no limit on the total number of files."
    },
]