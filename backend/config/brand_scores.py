"""
Brand Reputation Scores for Intelligent Product Ranking Engine.

Scale: 1 to 10.
Higher score = stronger brand reputation and quality trust.
Default fallback for unlisted / unknown brands = 4.
"""

from typing import Dict, Any

BRAND_SCORES: Dict[str, float] = {
    # Top Tier Tech / Premium Brands (10)
    "APPLE": 10.0,
    "SAMSUNG": 10.0,
    "SONY": 10.0,
    
    # Tier 1 Brands (9)
    "DELL": 9.0,
    "HP": 9.0,
    "LENOVO": 9.0,
    "ASUS": 9.0,
    "ONEPLUS": 9.0,
    "CANON": 9.0,
    "NIKON": 9.0,
    "BOSE": 9.0,
    "NIKE": 9.0,
    "ADIDAS": 9.0,
    "PUMA": 9.0,
    "ASICS": 9.0,
    "LEVI'S": 9.0,
    "LEVIS": 9.0,
    "PHILIPS": 9.0,
    "PRESTIGE": 9.0,
    "HAWKINS": 9.0,
    "YONEX": 9.0,
    "SPEEDO": 9.0,
    "WILSON": 9.0,
    "O'REILLY": 9.0,
    "PEARSON": 9.0,
    "MCGRAW HILL": 9.0,
    "PENGUIN": 9.0,
    "WILEY": 9.0,
    "HARPERCOLLINS": 9.0,
    "OXFORD": 9.0,
    
    # Strong / Tier 2 Brands (8)
    "LG": 8.0,
    "WHIRLPOOL": 8.0,
    "PANASONIC": 8.0,
    "HAVELLES": 8.0,
    "HAVELLS": 8.0,
    "WIPRO": 8.0,
    "WAKEFIT": 8.0,
    "BOMBAY DYEING": 8.0,
    "BOROSIL": 8.0,
    "MILTON": 8.0,
    "CELLO": 8.0,
    "WONDERCHEF": 8.0,
    "KENT": 8.0,
    "AGARO": 8.0,
    "USHA": 8.0,
    "CROMPTON": 8.0,
    "NIVIA": 8.0,
    "COSCO": 8.0,
    "DECATHLON": 8.0,
    "SPALDING": 8.0,
    "LI-NING": 8.0,
    "SHIMANO": 8.0,
    "BOLDFIT": 8.0,
    "STRAUSS": 8.0,
    "HEAD": 8.0,
    "SIMON & SCHUSTER": 8.0,
    "HACHETTE": 8.0,
    "ARIHANT": 8.0,
    "DISHA": 8.0,
    "NOTION PRESS": 8.0,
    "POLO": 8.0,
    "POLO RALPH LAUREN": 8.0,
    "U.S. POLO ASSN.": 8.0,
    "L'OREAL": 8.0,
    "LOREAL": 8.0,
    "MAYBELLINE": 8.0,
    "NIVEA": 8.0,
    "NEUTROGENA": 8.0,
    "CETAPHIL": 8.0,
    
    # Reliable / Tier 3 Brands (7)
    "ACER": 7.0,
    "BOAT": 7.0,
    "REALME": 7.0,
    "XIAOMI": 7.0,
    "REDMI": 7.0,
    "NOISE": 7.0,
    "FIRE-BOLTT": 7.0,
    "BOULT": 7.0,
    "PIGEON": 7.0,
    "BAJAJ": 7.0,
    "SOLIMO": 7.0,
    "SPOTZERO": 7.0,
    "MAMAEARTH": 7.0,
    "DOT & KEY": 7.0,
    "PLUM": 7.0,
    "SUGAR": 7.0,
    "HIMALAYA": 7.0,
    "COOFANDY": 7.0,
    "AMAZON BASICS": 7.0,
    
    # Budget / Value Brands (5 - 6)
    "ZEBRONICS": 6.0,
    "AMBRANE": 6.0,
    "PORTTRONICS": 6.0,
    "LIFELONG": 6.0,
    "BUTTERFLY": 6.0,
    "GENERIC": 5.0,
}

# Default score for unlisted or unknown brands
DEFAULT_BRAND_SCORE: float = 5.0


def get_brand_score(brand: str) -> float:
    """
    Look up brand reputation score from BRAND_SCORES.
    Normalizes brand string (upper case, clean spaces).
    Matches exact brand, or falls back to partial match, or DEFAULT_BRAND_SCORE (5.0).
    """
    if not brand or not isinstance(brand, str):
        return DEFAULT_BRAND_SCORE
    
    clean_brand = brand.strip().upper()
    
    # Clean prefix like "Brand: "
    if clean_brand.startswith("BRAND:"):
        clean_brand = clean_brand.replace("BRAND:", "").strip()
        
    # Exact match
    if clean_brand in BRAND_SCORES:
        return BRAND_SCORES[clean_brand]
    
    # Substring match (e.g. "Apple iPhone" -> "APPLE", "Dell Inspiron" -> "DELL")
    for known_brand, score in BRAND_SCORES.items():
        if known_brand in clean_brand or clean_brand in known_brand:
            return score
            
    return DEFAULT_BRAND_SCORE


def get_normalized_brand_score(brand: str) -> float:
    """Returns brand score normalized to [0.0, 1.0] range."""
    return get_brand_score(brand) / 10.0
