import cv2
import numpy as np
import os
import json

from skimage.metrics import structural_similarity as ssim
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import difflib # para comparação de strings

# 1. NORMALIZE SIGNATURE
def normalize_signature(image_path):
    """
    Loads and normalizes a signature:
    - grayscale
    - binarize
    - morphology closing (fix broken strokes)
    - crop to content
    - center on a fixed canvas
    - resize to consistent size
    """

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # 1. Binarize (invert so ink = white)
    _, th = cv2.threshold(
        img, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 2. Morphology closing to connect broken strokes
    kernel = np.ones((5, 15), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)

    # 3. Find contours
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        # fallback: resize original
        resized = cv2.resize(img, (600, 180), interpolation=cv2.INTER_AREA)
        return resized

    # 4. Bounding box around all contours
    x, y, w, h = cv2.boundingRect(np.vstack(contours))
    cropped = img[y:y+h, x:x+w]

    # 5. Resize cropped signature (preserving aspect ratio)
    target_w, target_h = 600, 180
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 6. Center the resized signature on a fixed canvas
    canvas = np.ones((target_h, target_w), dtype=np.uint8) * 255
    y_offset = (target_h - new_h) // 2
    x_offset = (target_w - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    return canvas


# 2. SEGMENT LETTERS
# ---------------------------------------------------------
def segment_letters(img):
    """
    Splits a normalized signature into individual letters.
    Returns a list of letter images ordered left-to-right.
    """

    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    letters = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        # Filter out noise
        if w < 5 or h < 20:
            continue

        letter = img[y:y+h, x:x+w]
        letters.append((x, letter))

    # Sort by x position (left to right)
    letters.sort(key=lambda x: x[0])

    return [l for _, l in letters]

# 3. COMPARE LETTERS
# ---------------------------------------------------------
def compare_letters(letters1, letters2):
    """
    Compares two lists of letters using template matching.
    Returns similarity 0–100.
    """

    if len(letters1) == 0 or len(letters2) == 0:
        return 0

    n = min(len(letters1), len(letters2))
    scores = []

    for i in range(n):
        l1 = cv2.resize(letters1[i], (40, 60))
        l2 = cv2.resize(letters2[i], (40, 60))

        res = cv2.matchTemplate(l1, l2, cv2.TM_CCOEFF_NORMED)
        scores.append(res.max())

    return round(sum(scores) / len(scores) * 100, 2)


# 4. MAIN COMPARISON FUNCTION
# ---------------------------------------------------------
def compare_signatures_letters(img1, img2):
    """
    Full signature comparison based on letter shapes.
    """

    letters1 = segment_letters(img1)
    letters2 = segment_letters(img2)

    return compare_letters(letters1, letters2)

# 5. EXTRACT FEATURES (wrapper)
# ---------------------------------------------------------
def extract_features(image_path):
    img = normalize_signature(image_path)

    # Quality check: enough ink pixels
    non_white = cv2.countNonZero(255 - img)
    quality_good = non_white > 300

    return img, quality_good

def compare_ssim(img1, img2):
    img1 = cv2.resize(img1, (400, 120))
    img2 = cv2.resize(img2, (400, 120))
    score, _ = ssim(img1, img2, full=True)
    return score * 100

def compare_ssim_full(img1, img2):
    img1 = cv2.resize(img1, (600, 180))
    img2 = cv2.resize(img2, (600, 180))
    score, _ = ssim(img1, img2, full=True)
    return score * 100

def compare_template_full(img1, img2):
    img1 = cv2.resize(img1, (600, 180))
    img2 = cv2.resize(img2, (600, 180))

    res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    return float(res.max() * 100)

def is_cursive(img):
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Assinaturas cursivas tendem a ter 1–3 contornos grandes
    return len(contours) <= 3

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return ""

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # aumentar contraste
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

    # remover ruído
    gray = cv2.GaussianBlur(gray, (1, 1), 0)

    # binarizar forte
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # dilatar ligeiramente para engrossar letras
    kernel = np.ones((2, 2), np.uint8)
    th = cv2.dilate(th, kernel, iterations=1)

    # OCR com modo de linha única
    text = pytesseract.image_to_string(th, config="--psm 7 -l eng")

    return text.strip()


def compare_by_ocr(query_signature_path, name_map):
    """
    If the signature is typed text (like 'Mark Stevens'),
    OCR will detect the name and match directly.
    """

    text = extract_text_from_image(query_signature_path)
    if not text:
        return None  # OCR falhou

    text_clean = text.lower().replace("\n", " ").strip()

    # Procurar nome correspondente na base de dados
    best_match = None
    best_score = 0

    for filename, person_name in name_map.items():
        score = difflib.SequenceMatcher(None, person_name.lower(), text_clean).ratio()
        if score > best_score:
            best_score = score
            best_match = person_name

    # Se a similaridade for aceitável (>= 0.4), devolve o nome
    if best_score >= 0.6: 
        return best_match, best_score * 100

    return None


# 6. COMPARE ALL SIGNATURES IN DB
def compare_all_signatures(query_signature_path, database_path="../generated_signatures"):
    """
    Hybrid signature comparison:
    - First try OCR (for typed signatures)
    - If OCR fails, fallback to visual matching
    """

    # Load name mapping
    mapping_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "signature_names.json"))
    with open(mapping_path, "r", encoding="utf-8") as f:
        name_map = json.load(f)

    # 1. Tentar OCR primeiro
    ocr_match = compare_by_ocr(query_signature_path, name_map)
    if ocr_match:
        name, score = ocr_match
        return {"top_3_matches": [(name, score)]}
    
    # Se o OCR devolveu texto mas não encontrou nome, não usar método visual
    if text := extract_text_from_image(query_signature_path):
        if any(c.isalpha() for c in text):
            # É texto, mas não corresponde a ninguém
            return {"top_3_matches": [("Texto detectado mas não corresponde a nenhum nome", 0)]}


    # 2. Se OCR falhar, usar o método visual (o teu pipeline atual)
    query_img, quality = extract_features(query_signature_path)
    if not quality:
        return {"status": "error", "message": "Signature quality too low."}

    query_is_cursive = is_cursive(query_img)

    results = []

    for filename in os.listdir(database_path):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        file_path = os.path.join(database_path, filename)
        db_img, db_quality = extract_features(file_path)

        db_is_cursive = is_cursive(db_img)

        # --- Cursive signatures: global comparison ---
        if query_is_cursive or db_is_cursive:
            similarity = compare_template_full(query_img, db_img)

        # --- Non-cursive: letter-based + SSIM ---
        else:
            similarity = compare_signatures_letters(query_img, db_img)

        results.append((filename, similarity))

    # Sort by similarity
    results.sort(key=lambda x: x[1], reverse=True)
    top_3 = results[:3]

    # Load name mapping
    mapping_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "signature_names.json"))
    with open(mapping_path, "r", encoding="utf-8") as f:
        name_map = json.load(f)

    top_3_named = [(name_map.get(f, "Unknown"), score) for f, score in top_3]

    return {"top_3_matches": top_3_named}

