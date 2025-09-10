from typing import List,Dict,Tuple
from pypdf import PdfReader
import re

#extract text from pdf
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    texts: List[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)

EXPECTED_KEYS = {
    "pregnancies": r"(?:pregnancies?|preg)\s*[:=-]?\s*(\d+)",
    "glucose": r"(?:glucose|glu)\s*[:=-]?\s*(\d+(?:\.\d+)?)",
    "blood_pressure": r"(?:blood\s*pressure|bp|bloodpressure)\s*[:=-]?\s*(\d+(?:\.\d+)?)",
    "skin_thickness": r"(?:skin\s*thickness|skin|skinthickness)\s*[:=-]?\s*(\d+(?:\.\d+)?)",
    "insulin": r"(?:insulin|ins)\s*[:=-]?\s*(\d+(?:\.\d+)?)",
    "bmi": r"(?:bmi|body\s*mass\s*index)\s*[:=-]?\s*(\d+(?:\.\d+)?)",  
    "diabetes_pedigree_function": r"(?:dpf|diabetes\s*pedigree\s*function|pedigree)\s*[:=-]?\s*(\d+(?:\.\d+)?)",
    "age": r"(?:age)\s*[:=-]?\s*(\d+)",
}


def extract_features(text: str) -> Dict[str, float]:
    """Extract diabetes features from text. Returns empty dict if no features found."""
    text_lower = text.lower()
    features: Dict[str, float] = {}
    missing_features: List[str] = []

    for key, pattern in EXPECTED_KEYS.items():
        match = re.search(pattern, text_lower)
        if match:
            try:
                value_str = match.group(1) if key != "diabetes_pedigree_function" else match.group(1)
                features[key] = float(value_str)
            except (ValueError, IndexError):
                missing_features.append(key)
        else:
            missing_features.append(key)

    return features


def extract_features_with_validation(text: str) -> tuple[Dict[str, float], List[str]]:
    """Extract features and return both features and missing features list."""
    features = extract_features(text)
    missing_features = [key for key in EXPECTED_KEYS.keys() if key not in features]
    return features, missing_features



    