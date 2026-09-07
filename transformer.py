"""Message transformer and filter for Bhola Updates forwarder bot.

Targets and transforms only the 5 specified message types:
1. ALL RESULTS summary (removes SUPREME markets, converts headers, strips bhai links)
2. Single Market Fast Update (e.g. TIME BAZAR, KALYAN, etc. with result box or digits)
3. Good Night greeting -> Custom Good Night message
4. Good Morning greeting -> Custom Good Morning message
5. Promo / App download ad -> Custom Bhola Ji Office rates & contact promo

All other messages are ignored (skipped).
"""
import re

PROMO_DESTINATION_TEMPLATE = """BHOLA JI OFFICE
CUTTING CONTACT := 7697113466 💬
*──────⊱◈◈◈⊰──────*
सबसे ज्यादा रेट के साथ ऑनलाइन खेले और दिन मै अपनी जीती हुई राशि निकले*
💵*सिंगल अंक 100रु का 1000रु*
💵*जोड़ी 100रु का 10000रु*
💵*सिंगल पाना का 100रु का 15000रु*
💵*डबल पाना का 100रु का 30000रु*
💵*ट्रिपल पाना का 100रु का 50000रु*
💵*आधा संगम का 10रु का 10000रु*
💵*पुरा संगम का 10रु का 100000रु*"""

GOOD_NIGHT_TEMPLATE = """😴 GOOD NIGHT 😴
KAL PHIR SE NAYE SHURUAAT"""

GOOD_MORNING_TEMPLATE = """🌄 GOOD MORNING 🌄"""

EXCLUDED_MARKETS = {"SUPREME DAY", "SUPREME NIGHT", "SUPREME"}

KNOWN_MARKETS = [
    "TIME BAZAR", "MADHUR DAY", "MADHUR NIGHT", "MILAN DAY", "MILAN NIGHT",
    "RAJDHANI DAY", "RAJDHANI NIGHT", "KALYAN", "KALYAN NIGHT", "SRIDEVI NIGHT",
    "SRIDEVI", "MAIN BAZAR", "SUPREME DAY", "SUPREME NIGHT", "KUBER DAY", "KUBER NIGHT",
    "OLD MAIN MUMBAI", "KALYAN MORNING", "MADHUR MORNING", "SRIDEVI MORNING"
]

def transform_all_results(text: str) -> str | None:
    """Matches and transforms ALL RESULTS summary."""
    upper = text.upper()
    if "ALL RESULTS" not in upper and "DAY RESULTS" not in upper and "NIGHT RESULTS" not in upper:
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    output_lines = ["🔱BHOLA UPDATES🔱"]

    for line in lines:
        u = line.upper()

        # Date line e.g., 19/08/2026 (WEDNESDAY)
        if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', line):
            output_lines.append(line)
            continue

        if "ALL RESULTS" in u:
            output_lines.append("ALL RESULTS")
            continue

        if "DAY RESULTS" in u:
            output_lines.append("🌞DAY RESULTS🌞")
            continue

        if "NIGHT RESULTS" in u:
            output_lines.append("🌕NIGHT RESULTS🌕")
            continue

        # Skip URLs / download links / bot promos
        if "http://" in line or "https://" in line or "bhai567" in line.lower() or "t.me/" in line.lower():
            continue

        # Header emojis / symbols skip
        if any(char in line for char in ["🔠", "5️⃣", "6️⃣", "7️⃣", "〰️"]):
            continue

        # Market line matching (e.g. "SRIDEVI 400-49-360" or "TIME BAZAR 149-46-556" or partial)
        market_match = re.match(r'^([A-Za-z\s]+?)\s+([\d\*\?]+(?:-[\d\*\?]+)*)$', line)
        if market_match:
            market_name = market_match.group(1).strip()
            result_num = market_match.group(2).strip()

            if market_name.upper() in EXCLUDED_MARKETS:
                continue

            output_lines.append(f"{market_name} {result_num}")
            continue

    output_lines.append("🔱BHOLA UPDATES🔱")
    return "\n".join(output_lines)

def transform_single_market(text: str) -> str | None:
    """Matches and transforms single market fast update (full result or open/close ank)."""
    # If it's the ALL RESULTS table, don't parse as single market
    upper = text.upper()
    if "ALL RESULTS" in upper or "DAY RESULTS" in upper or "NIGHT RESULTS" in upper:
        return None

    # Find result digits anywhere in the message
    result_digits = None

    # Case 1: Inside target emoji 🎯 126 - 90 - 127 🎯
    box_match = re.search(r'🎯\s*([\d\s\-]+?)\s*🎯', text)
    if box_match:
        result_digits = box_match.group(1).strip()
    else:
        # Case 2: Standard result formats like:
        # 126-90-127, 126 - 90 - 127, 126-90, 126-9-, 126-9, 126 - 9
        digit_match = re.search(r'\b(\d{3}\s*-\s*\d{1,3}\s*-\s*\d{1,3}|\d{3}\s*-\s*\d{1,3}\s*-|\d{3}\s*-\s*\d{1,3}|\d{1,3}\s*-\s*\d{1,3}\s*-\s*\d{1,3})\b', text)
        if digit_match:
            result_digits = digit_match.group(1).strip()

    if not result_digits:
        return None

    # Format result digits with double dash: "126 -- 90 -- 127"
    parts = re.split(r'\s*[-]+\s*', result_digits)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) >= 2:
        formatted_digits = " -- ".join(parts)
    else:
        formatted_digits = result_digits

    # Detect Market Name
    detected_market = None
    for km in KNOWN_MARKETS:
        if km in upper:
            detected_market = km
            break

    if not detected_market:
        # Fallback: scan lines for any clean text
        for l in text.splitlines():
            clean_l = re.sub(r'[🔥💰🎯⚡🚀•\s\─\✦\╭\╰\=\-\>\<\?]+', ' ', l).strip()
            if clean_l and not any(k in clean_l.upper() for k in ["SUPER FAST", "FASTEST", "FAST UPDATE", "UPDATE", "सबसे पहले", "BHOLA", "BHAI", "LIVE"]):
                detected_market = clean_l
                break

    if not detected_market:
        return None  # No recognizable market name

    output = f"💰{detected_market} 💰\n╭───── ✦ ─────╮\n🎯 {formatted_digits} 🎯\n╰───── ✦ ─────╯\n🔱BHOLA UPDATES🔱"
    return output

def transform_good_night(text: str) -> str | None:
    """Matches Good Night messages."""
    upper = text.upper()
    if "GOOD NIGHT" in upper or "AARAM SE SOYEIN" in upper or "KAL MILTE HAIN NAYE RESULT" in upper or "SOYEIN" in upper or "SHUBHRATRI" in upper:
        return GOOD_NIGHT_TEMPLATE
    return None

def transform_good_morning(text: str) -> str | None:
    """Matches Good Morning messages."""
    upper = text.upper()
    if "GOOD MORNING" in upper or ("NAYA DIN" in upper and "NAYA RESULT" in upper) or "NAYA LUCK" in upper or "SHUBH PRABHAT" in upper:
        return GOOD_MORNING_TEMPLATE
    return None

def transform_promo(text: str) -> str | None:
    """Matches Bhai 567 / Matka Application Promo messages."""
    lower = text.lower()
    if (
        "bhai567" in lower
        or "भरोसेमंद मटका" in text
        or "gujrat no.1" in lower
        or "download link" in lower
        or "डाउनलोड करिए" in text
        or "matka application" in lower
        or "deposit" in lower
        or "withdrawal" in lower
    ):
        return PROMO_DESTINATION_TEMPLATE
    return None

def process_message(text: str | None) -> tuple[bool, str | None]:
    """Process incoming message from Source Channel.
    
    Returns:
        (should_forward: bool, transformed_text: str | None)
        If should_forward is False, the message is ignored.
    """
    if not text or not text.strip():
        return False, None

    # 1. Good Morning
    res = transform_good_morning(text)
    if res:
        return True, res

    # 2. Good Night
    res = transform_good_night(text)
    if res:
        return True, res

    # 3. ALL RESULTS Summary
    res = transform_all_results(text)
    if res:
        return True, res

    # 4. Single Market Fast Update
    res = transform_single_market(text)
    if res:
        return True, res

    # 5. Promo / App Download Ad
    res = transform_promo(text)
    if res:
        return True, res

    # Ignore all other messages
    return False, None
