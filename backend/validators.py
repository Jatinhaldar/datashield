"""
Validation utility functions for sensitive data identifiers.
Includes Verhoeff (Aadhaar) and Luhn (Credit Card) algorithms.
"""

# --- Verhoeff Algorithm for Aadhaar ---
# Multiplication table
VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

# Permutation table
VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

# Inverse table
VERHOEFF_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

def is_valid_aadhaar(number: str) -> bool:
    """Validate Aadhaar number using Verhoeff algorithm."""
    # Clean the number (remove spaces/dashes)
    number = "".join(filter(str.isdigit, number))
    if len(number) != 12:
        return False
    
    # Verhoeff calculation
    checksum = 0
    for i, digit in enumerate(reversed(number)):
        checksum = VERHOEFF_D[checksum][VERHOEFF_P[i % 8][int(digit)]]
    
    return checksum == 0

# --- Luhn Algorithm for Credit Cards ---
def is_valid_luhn(number: str) -> bool:
    """Validate number using Luhn algorithm."""
    # Clean the number
    number = "".join(filter(str.isdigit, number))
    if not (13 <= len(number) <= 19):
        return False
        
    digits = [int(d) for d in number]
    checksum = digits[-1]
    payload = digits[:-1]
    
    total = 0
    for i, digit in enumerate(reversed(payload)):
        if i % 2 == 0:
            doubled = digit * 2
            total += doubled if doubled < 10 else doubled - 9
        else:
            total += digit
            
    return (total + checksum) % 10 == 0

def is_valid_pan(pan: str) -> bool:
    """Basic structural validation for Indian PAN card."""
    import re
    # PAN format: 5 letters, 4 digits, 1 letter
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    return bool(re.match(pattern, pan.upper()))

def get_validator_for_label(label: str):
    """Return the validation function for a given data label."""
    mapping = {
        "AADHAAR_12_DIGIT": is_valid_aadhaar,
        "CREDIT_CARD": is_valid_luhn,
        "PAN_CARD": is_valid_pan
    }
    return mapping.get(label)
