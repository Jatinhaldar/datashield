import re

class DataShield:
    def __init__(self):
        # Regex patterns for basic sensitive data
        self.patterns = {
            "PHONE_NUMBER": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }

    def mask_data(self, text: str) -> str:
        masked_text = text
        for label, pattern in self.patterns.items():
            masked_text = re.sub(pattern, f"<{label}>", masked_text)
        return masked_text
