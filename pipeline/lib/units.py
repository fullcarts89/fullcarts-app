"""Unit parsing and normalization for package weights.

Handles formats from USDA FoodData Central, Kroger, Open Food Facts, etc:
  - "6 oz/170 g"
  - "16 OZ"
  - "1 LB 4 OZ"
  - "340g"
  - "6 oz (170g)"
  - "2.5 kg"
  - "12 FL OZ"
"""
import re
from typing import Optional, Tuple

# ── Unit normalization map ────────────────────────────────────────────────────

UNIT_MAP = {
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "fl oz": "fl oz",
    "fl. oz": "fl oz",
    "fl.oz": "fl oz",
    "fluid ounce": "fl oz",
    "fluid ounces": "fl oz",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "ml": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "l": "l",
    "liter": "l",
    "liters": "l",
    "ct": "ct",
    "count": "ct",
    "pack": "ct",
    "pcs": "ct",
    "pieces": "ct",
    "piece": "ct",
    "sheets": "sheets",
    "sheet": "sheets",
    "rolls": "rolls",
    "roll": "rolls",
    "pt": "pt",
    "pint": "pt",
    "pints": "pt",
    "qt": "qt",
    "quart": "qt",
    "quarts": "qt",
    "gal": "gal",
    "gallon": "gal",
    "gallons": "gal",
    "sq ft": "sq ft",
    "sq. ft": "sq ft",
    # USDA FoodData Central ISO unit codes
    "onz": "oz",
    "lbr": "lb",
    "grm": "g",
    "kgm": "kg",
    "mlt": "ml",
    "ltr": "l",
    "flo": "fl oz",
    "gll": "gal",
    "ptn": "pt",
    "qrt": "qt",
}

# ── Conversion factors (to base units) ───────────────────────────────────────

CONVERSIONS = {
    "kg": ("g", 1000),
    "l": ("ml", 1000),
    "lb": ("oz", 16),
    "gal": ("fl oz", 128),
    "qt": ("fl oz", 32),
    "pt": ("fl oz", 16),
}

# ── Regex patterns ────────────────────────────────────────────────────────────

# Matches a number + unit token, e.g. "6 oz", "340g", "2.5 kg", "12 FL OZ"
_NUM_UNIT = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    # USDA FDC 3-letter codes first (must precede short forms like g, l)
    r"(onz|lbr|kgm|grm|mlt|ltr|flo|gll|ptn|qrt|"
    r"fl\.?\s*oz|fluid\s+ounces?|"
    r"oz|ounces?|"
    r"lbs?|pounds?|"
    r"kg|kilograms?|"
    r"g|grams?|"
    r"ml|milliliters?|"
    r"l|liters?|"
    r"ct|count|pack|pcs|pieces?|"
    r"sheets?|rolls?|"
    r"sq\.?\s*ft|"
    r"pt|pints?|qt|quarts?|gal|gallons?)",
    re.IGNORECASE,
)

# Matches compound weights like "1 LB 4 OZ"
_COMPOUND_LB_OZ = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds)\s+"
    r"(\d+(?:\.\d+)?)\s*(?:oz|ounce|ounces)",
    re.IGNORECASE,
)


def normalize_unit(u: str) -> str:
    """Normalize a unit string to its canonical short form."""
    if not u:
        return "oz"
    key = " ".join(u.lower().split())  # Collapse whitespace
    # Try direct lookup
    result = UNIT_MAP.get(key)
    if result:
        return result
    # Try stripping trailing 's'
    result = UNIT_MAP.get(key.rstrip("s"))
    if result:
        return result
    return key


def parse_package_weight(text: str) -> Tuple[Optional[float], Optional[str]]:
    """Parse a free-text package weight into (numeric_value, unit).

    Returns (None, None) if the text cannot be parsed.

    Strategy:
      1. Try compound "1 LB 4 OZ" → convert to total oz
      2. Try slash-separated "6 oz/170 g" → take first (US) value
      3. Try parenthetical "6 oz (170g)" → take first value
      4. Try simple "340g" or "16 OZ"
    """
    if not text or not text.strip():
        return None, None

    text = text.strip()

    # Step 1: Compound "1 LB 4 OZ"
    m = _COMPOUND_LB_OZ.search(text)
    if m:
        lb_val = float(m.group(1))
        oz_val = float(m.group(2))
        total_oz = lb_val * 16 + oz_val
        return total_oz, "oz"

    # Step 2: Slash-separated "6 oz/170 g" → take the first one
    if "/" in text:
        parts = text.split("/", 1)
        val, unit = _parse_single(parts[0].strip())
        if val is not None:
            return val, unit
        # Try the second part if first failed
        val, unit = _parse_single(parts[1].strip())
        if val is not None:
            return val, unit

    # Step 3: Parenthetical "6 oz (170g)" → take content before parens
    if "(" in text:
        before_paren = text.split("(", 1)[0].strip()
        val, unit = _parse_single(before_paren)
        if val is not None:
            return val, unit

    # Step 4: Simple pattern "340g", "16 OZ"
    return _parse_single(text)


def _parse_single(text: str) -> Tuple[Optional[float], Optional[str]]:
    """Parse a single number+unit from text."""
    m = _NUM_UNIT.search(text)
    if not m:
        return None, None
    value = float(m.group(1))
    unit = normalize_unit(m.group(2))
    return value, unit


def convert_to_base(value: float, unit: str) -> Tuple[float, str]:
    """Convert to a base unit for comparison (kg→g, lb→oz, etc.).

    Returns (converted_value, base_unit). If no conversion needed,
    returns the original value and unit.
    """
    if unit in CONVERSIONS:
        base_unit, factor = CONVERSIONS[unit]
        return value * factor, base_unit
    return value, unit
