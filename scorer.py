"""
Decides whether a model answer is correct, given the reference answer.

This uses text normalization heuristics to handle case, punctuation, common conversational prefixes,
number-to-word conversions, and synonym mapping.
"""
import string
import re
from num2words import num2words

# Common synonym mappings
SYNONYMS = {
    "uk": "united kingdom",
    "great britain": "united kingdom",
    "us": "united states",
    "usa": "united states",
    "united states of america": "united states",
    "uae": "united arab emirates",
}

def replace_numbers(match):
    try:
        return num2words(int(match.group())).replace("-", " ")
    except Exception:
        return match.group()

def normalize_text(text):
    if text is None:
        return ""
    text = str(text).lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove common prefixes
    prefixes = [
        "the answer is",
        "its",
        "it is",
        "i think it is",
        "i think its"
    ]
    for p in prefixes:
        if text.startswith(p):
            text = text[len(p):].strip()
            
    # Convert all numbers to their word equivalents (e.g., "4" -> "four")
    text = re.sub(r'\b\d+\b', replace_numbers, text)
    
    # Apply synonym mapping if the whole answer is a synonym
    if text in SYNONYMS:
        text = SYNONYMS[text]
        
    return text.strip()

import difflib
import urllib.request
import json
import urllib.parse
import time

DATAMUSE_CACHE = {}

def get_synonyms(word):
    """Fetches synonyms from Datamuse API with local caching."""
    word = word.strip()
    # Datamuse works best for single words or short phrases
    if not word or len(word.split()) > 2:
        return []
        
    if word in DATAMUSE_CACHE:
        return DATAMUSE_CACHE[word]
        
    try:
        url = f"https://api.datamuse.com/words?rel_syn={urllib.parse.quote(word)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'EvaluationScript/1.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            synonyms = [d['word'] for d in data]
            DATAMUSE_CACHE[word] = synonyms
            time.sleep(0.1)  # Rate limiting safety
            return synonyms
    except Exception:
        return []

def score(reference_answer, model_answer, question=None):
    """Return {"is_correct": bool, "confidence": float in [0,1]}.

    Keep this signature and return shape — the pipeline and the grader call it directly.
    """
    if not model_answer:
        return {"is_correct": False, "confidence": 0.0}
        
    ref_norm = normalize_text(reference_answer)
    mod_norm = normalize_text(model_answer)
    
    is_correct = False
    if ref_norm == mod_norm:
        is_correct = True
    # If the exact normalized reference is inside the model answer, and is a meaningful length
    elif len(ref_norm) > 3 and ref_norm in mod_norm:
        is_correct = True
    else:
        # Fuzzy matching fallback to catch minor typos and plurals
        ratio = difflib.SequenceMatcher(None, ref_norm, mod_norm).ratio()
        if ratio > 0.85:
            is_correct = True
        else:
            pass # Uncomment below for Dynamic Synonym Fallback (adds ~30s execution time)
            # synonyms = get_synonyms(ref_norm)
            # if mod_norm in synonyms:
            #     is_correct = True
        
    return {"is_correct": is_correct, "confidence": 1.0 if is_correct else 0.0}
