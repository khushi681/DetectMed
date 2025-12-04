import re
from datetime import datetime, timedelta
from dateutil import parser as dparser

# Configuration / thresholds
EXPIRY_SOON_DAYS = 60
EARLIEST_YEAR = 1900
LATEST_YEAR = 2100

# Helper: convert two-digit year sensibly to 4-digit
def fix_two_digit_year(y):
    y = int(y)
    if y < 100:
        # map 00-49 -> 2000-2049, 50-99 -> 1950-1999 (conservative)
        return 2000 + y if y <= 49 else 1900 + y
    return y

def normalize_text(input_text):
    """Turn OCR output (list or string) to a normalized single string."""
    if input_text is None:
        return ""
    if isinstance(input_text, (list, tuple)):
        s = " ".join([str(x) for x in input_text])
    else:
        s = str(input_text)
    # common OCR noise cleanup
    s = s.replace('|', '/')
    s = s.replace('\\', '/')
    s = s.replace('O', '0')  # sometimes O->0
    s = s.replace('o', '0')
    # remove weird characters except digits, letters, / - . : and space
    s = re.sub(r'[^0-9A-Za-z\/\-\.\:\s]', ' ', s)
    # collapse spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# Regex candidate patterns (order matters: more specific first)
DATE_PATTERNS = [
    # formats like EXP 10/25 or EXP: 10/25 or EXP 10/2025
    r'(?:exp|expiry|expir|use by|use-by|useby|bbe|exp\.|exp:)\s*[:\-]?\s*([0-3]?\d[\/\-\.\:][0-3]?\d[\/\-\.\:]\d{2,4})',
    r'(?:exp|expiry|expir|use by|use-by|useby|bbe|exp\.|exp:)\s*[:\-]?\s*([0-3]?\d[\/\-\.\:]\d{2,4})',
    r'(?:exp|expiry|use by|bbe)\s*[:\-]?\s*([A-Za-z]{3,9}\s*\d{2,4})',  # e.g., OCT 2026
    # bare date tokens
    r'([0-3]?\d[\/\-\.\:][0-3]?\d[\/\-\.\:]\d{2,4})',
    r'([0-3]?\d[\/\-\.\:]\d{2,4})',     # 10/2025 or 10/25
    r'([0-1]?\d[\/\-\.\:]\d{4})',      # mm/yyyy
    r'([A-Za-z]{3,9}\s*\d{2,4})',      # OCT 2026 or Oct 26
    r'\b(\d{4})\b'                     # year only
]

def try_parse_candidate(token):
    token_orig = token.strip()
    token = token_orig.replace('.', '/').replace(':', '/').replace('-', '/')
    token = token.strip()

    # If token is only year
    if re.fullmatch(r'\d{4}', token):
        y = int(token)
        if EARLIEST_YEAR <= y <= LATEST_YEAR:
            # assume end of year
            return datetime(y, 12, 31)

    # If token like dd/mm/yy or dd/mm/yyyy or dd/mm
    m = re.match(r'^([0-3]?\d)\/([0-3]?\d)\/(\d{2,4})$', token)
    if m:
        d, mo, y = m.groups()
        d = int(d); mo = int(mo); y = int(y)
        if y < 100:  # two-digit
            y = fix_two_digit_year(y)
        try:
            return datetime(y, mo, d)
        except Exception:
            return None

    # If token like dd/mm or mm/yy or mm/yyyy
    m2 = re.match(r'^([0-3]?\d)\/(\d{2,4})$', token)
    if m2:
        part1, part2 = m2.groups()
        # Could be dd/yy or mm/yyyy or mm/yy
        # Heuristic: if part1>12 treat part1 as day
        p1 = int(part1); p2 = int(part2)
        # If p2 is 4-digit -> assume month/year
        if len(part2) == 4:
            mo = p1
            y = p2
            if 1 <= mo <= 12:
                try:
                    return datetime(int(y), mo, 1)
                except:
                    return None
        else:
            # two-digit year -> map
            y = fix_two_digit_year(p2)
            # try both interpretations: treat p1 as month then as day
            # prefer sensible month (1-12)
            if 1 <= p1 <= 12:
                try:
                    return datetime(y, p1, 1)
                except:
                    pass
            # if p1 > 12, maybe it's day/month swapped -> can't resolve reliably
            # fallback: assume day=1, month=1
            try:
                return datetime(y, 1, 1)
            except:
                return None

    # If token like "OCT 2026" or "Oct 26"
    m3 = re.match(r'^([A-Za-z]{3,9})\s*\.?\s*(\d{2,4})$', token)
    if m3:
        mon_str, y = m3.groups()
        try:
            y = int(y)
            if y < 100:
                y = fix_two_digit_year(y)
            # parse month name
            dt = dparser.parse(f'1 {mon_str} {y}', dayfirst=False, fuzzy=True)
            return datetime(dt.year, dt.month, 1)
        except Exception:
            return None

    # Last resort: use dateutil fuzzy parsing
    try:
        # allow dayfirst - many labels use day/month
        dt = dparser.parse(token, dayfirst=True, fuzzy=True)
        # sanity check
        if EARLIEST_YEAR <= dt.year <= LATEST_YEAR:
            return dt
    except Exception:
        return None

    return None

def select_best_date(candidates):
    """Given a list of datetime objects, select the most plausible expiry date."""
    if not candidates:
        return None
    # Prefer future dates (valid/expiring soon). If all past choose the most recent past.
    today = datetime.today()
    future = [d for d in candidates if d >= today - timedelta(days=1)]
    if future:
        # choose the nearest future (earliest future)
        return min(future)
    # otherwise return the latest past date (most recent)
    return max(candidates)

def parse_expiry_date(ocr_text):
    """
    Input: ocr_text (string or list)
    Output: (status_string, display_date_string)
    status_string in {"EXPIRED","EXPIRING SOON","VALID","UNKNOWN"}
    display_date_string: human-friendly (YYYY-MM-DD) or extracted token
    """
    text = normalize_text(ocr_text)
    if not text:
        return "UNKNOWN", "None"

    # Collect tokens that look like dates
    tokens = []
    # First, if we see explicit words near dates, capture stronger tokens
    for pat in DATE_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            grp = m.group(1)
            if grp:
                tokens.append(grp.strip())

    # If none found, also pull digit groups loosely
    if not tokens:
        loose = re.findall(r'[0-9]{1,2}[\/\-\.\:][0-9A-Za-z]{1,6}[\/\-\.\:]*[0-9]{0,4}', text)
        tokens.extend(loose)

    # Deduplicate while preserving order
    seen = set()
    tokens_filtered = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            tokens_filtered.append(t)
    tokens = tokens_filtered

    # Try parsing each token into a datetime
    parsed = []
    parsed_map = {}
    for t in tokens:
        dt = try_parse_candidate(t)
        if dt is not None:
            parsed.append(dt)
            parsed_map[dt] = t

    # If nothing parsed, attempt fuzzy scan token by token
    if not parsed:
        words = text.split()
        for w in words:
            # simple digit heavy tokens only
            if re.search(r'\d', w):
                dt = try_parse_candidate(w)
                if dt:
                    parsed.append(dt)
                    parsed_map[dt] = w

    # If still nothing, return unknown with best fallback (maybe a year in text)
    if not parsed:
        # try find 4-digit year anywhere
        m = re.search(r'\b(19|20)\d{2}\b', text)
        if m:
            y = int(m.group(0))
            return "UNKNOWN", f"{y}"
        return "UNKNOWN", "None"

    # Choose best candidate
    best_dt = select_best_date(parsed)
    if best_dt is None:
        return "UNKNOWN", "None"

    # Prepare display string
    display = best_dt.strftime("%Y-%m-%d")

    # Determine status
    today = datetime.today()
    if best_dt < today:
        status = "EXPIRED"
    elif (best_dt - today).days <= EXPIRY_SOON_DAYS:
        status = "EXPIRING SOON"
    else:
        status = "VALID"

    return status, display
