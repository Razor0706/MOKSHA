import cv2
import pytesseract


def extract_text(filepath):
    image = cv2.imread(str(filepath))
    if image is None:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")

    image = cv2.resize(image, None, fx=1.8, fy=1.8, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresholded = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2,
    )

    text = pytesseract.image_to_string(thresholded, config="--psm 6")
    print("\n========== OCR TEXT FOR DEBUGGING ==========")
    print(text)
    print("===========================================\n")

    if len(text.strip()) < 10:
        raise ValueError("Unable to confidently extract values. Please upload a clearer report.")
    return text
