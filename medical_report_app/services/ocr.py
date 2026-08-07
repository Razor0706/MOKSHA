import cv2
import numpy as np
import pytesseract


def _resize_image(image):
    h, w = image.shape[:2]
    if w < 1000:
        return cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return image


def _to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _apply_clahe(gray_image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray_image)


def _denoise(gray_image):
    return cv2.GaussianBlur(gray_image, (3, 3), 0)


def _adaptive_threshold(gray_image):
    return cv2.adaptiveThreshold(
        gray_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )


def _deskew(binary_image):
    coords = np.column_stack(np.where(binary_image < 255))
    if len(coords) == 0:
        return binary_image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) > 45 or abs(angle) < 0.5:
        return binary_image

    height, width = binary_image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(binary_image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _score_ocr_text(text):
    return sum(character.isalnum() for character in text)


def extract_text(filepath):
    image = cv2.imread(str(filepath))
    if image is None:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")

    image = _resize_image(image)
    gray = _to_grayscale(image)
    contrast = _apply_clahe(gray)
    denoised = _denoise(contrast)
    thresholded = _adaptive_threshold(denoised)

    text = pytesseract.image_to_string(thresholded, config="--psm 6")

    if len(text.strip()) < 20:
        deskewed = _deskew(thresholded)
        alt_text = pytesseract.image_to_string(deskewed, config="--psm 6")
        if _score_ocr_text(alt_text) > _score_ocr_text(text):
            text = alt_text

    try:
        print("\n========== OCR TEXT FOR DEBUGGING ==========")
        print(text.encode("ascii", errors="replace").decode("ascii"))
        print("===========================================\n")
    except Exception:
        pass

    if len(text.strip()) < 10:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")
    return text
