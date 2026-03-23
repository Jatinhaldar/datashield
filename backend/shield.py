import re
from validators import get_validator_for_label

class DataShield:
    def __init__(self):
        # Regex patterns for basic sensitive data
        self.patterns = {
            # --- High Priority / Specific Identifiers ---
            "AADHAAR_12_DIGIT": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
            "PHONE_10_DIGIT": r"\b(?:\+91|0)?[6-9]\d{9}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PAN_CARD": r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",
            
            # --- Identity ---
            "PASSPORT_IN": r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b",
            "VOTER_ID": r"\b[A-Z]{3}\d{7}\b",
            "DL_NUMBER": r"\b[A-Z]{2}[0-9]{2}[0-9]{11}\b",
            
            # --- Financial ---
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "UPI_ID": r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b",
            "BANK_ACC": r"\b\d{9,18}\b",
            "CVV": r"(?i)\b(?:cvv|cvc)(?:\s+is)?[:\s]?\s?(\d{3,4})\b",
            
            # --- Security ---
            "API_KEY": r"\b(sk|key|token|api)[-_]?[0-9a-zA-Z]{32,64}\b",
            
            # --- Health Data ---
            "ABHA_ID": r"\b\d{2}-\d{4}-\d{4}-\d{4}\b",
            
            # --- Dates ---
            "DATE": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b"
        }

    def mask_data(self, text: str) -> str:
        masked_text = text
        for label, pattern in self.patterns.items():
            matches = list(re.finditer(pattern, masked_text))
            
            for match in sorted(matches, key=lambda m: m.start(), reverse=True):
                if match.groups():
                    full_match = match.group(0)
                    captured_val = match.group(1)
                    validate_fn = get_validator_for_label(label)
                    
                    if validate_fn and not validate_fn(captured_val):
                        continue
                        
                    start_idx, end_idx = match.start(1), match.end(1)
                else:
                    value = match.group()
                    validate_fn = get_validator_for_label(label)
                    
                    if validate_fn and not validate_fn(value):
                        continue
                    
                    start_idx, end_idx = match.start(), match.end()

                masked_text = (
                    masked_text[:start_idx] +
                    f"<{label}>" +
                    masked_text[end_idx:]
                )
        return masked_text
