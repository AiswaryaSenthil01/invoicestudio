"""
Convert monetary numbers to Indian English Words (Rupees & Paise)
Follows Indian numbering system (Lakhs, Crores).
"""

ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen"
]

TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"
]


def _two_digits_to_words(n: int) -> str:
    """Convert an integer between 0 and 99 into words."""
    if n == 0:
        return ""
    if n < 20:
        return ONES[n]
    tens_digit = n // 10
    ones_digit = n % 10
    if ones_digit == 0:
        return TENS[tens_digit]
    return f"{TENS[tens_digit]} {ONES[ones_digit]}"


def _three_digits_to_words(n: int) -> str:
    """Convert an integer between 0 and 999 into words."""
    hundreds = n // 100
    rem = n % 100
    res = []
    if hundreds > 0:
        res.append(f"{ONES[hundreds]} Hundred")
    if rem > 0:
        res.append(_two_digits_to_words(rem))
    return " ".join(res)


def integer_to_indian_words(n: int) -> str:
    """
    Convert an integer to Indian words using Crores, Lakhs, Thousands, Hundreds.
    """
    if n == 0:
        return "Zero"

    words = []

    # Crores (10,000,000)
    crores = n // 10000000
    rem = n % 10000000
    if crores > 0:
        words.append(f"{integer_to_indian_words(crores)} Crore")

    # Lakhs (100,000)
    lakhs = rem // 100000
    rem = rem % 100000
    if lakhs > 0:
        words.append(f"{_two_digits_to_words(lakhs)} Lakh")

    # Thousands (1,000)
    thousands = rem // 1000
    rem = rem % 1000
    if thousands > 0:
        words.append(f"{_two_digits_to_words(thousands)} Thousand")

    # Hundreds and below (1 to 999)
    if rem > 0:
        words.append(_three_digits_to_words(rem))

    return " ".join(words).strip()


def amount_to_words(amount: float) -> str:
    """
    Convert a numeric currency amount into formal Indian English wording.
    Example: 59000.00 -> 'Rupees Fifty Nine Thousand Only'
    Example: 12500.50 -> 'Rupees Twelve Thousand Five Hundred and Paise Fifty Only'
    """
    try:
        amt = round(float(amount), 2)
    except (ValueError, TypeError):
        return "Rupees Zero Only"

    if amt < 0:
        return f"Minus {amount_to_words(abs(amt))}"

    int_part = int(amt)
    paise_part = int(round((amt - int_part) * 100))

    rupees_str = integer_to_indian_words(int_part)

    if int_part == 0 and paise_part == 0:
        return "Rupees Zero Only"

    parts = []
    if int_part > 0:
        parts.append(f"Rupees {rupees_str}")
    elif paise_part > 0:
        parts.append("Rupees Zero")

    if paise_part > 0:
        paise_str = _two_digits_to_words(paise_part)
        parts.append(f"and Paise {paise_str}")

    parts.append("Only")
    return " ".join(parts)
