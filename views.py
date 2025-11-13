# # views.py
# import cv2
# import numpy as np
# import base64
# import re
# import pytesseract
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# # Set Tesseract path (Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# class CNICVerificationView(APIView):
#     def post(self, request):
#         try:
#             # Get base64 image string from request
#             image_base64 = request.data.get("image")
#             if not image_base64:
#                 return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

#             # Remove header "data:image/jpeg;base64," if present
#             if "," in image_base64:
#                 image_base64 = image_base64.split(",")[1]

#             # Decode base64 to bytes
#             image_bytes = base64.b64decode(image_base64)

#             # Convert to numpy array and OpenCV image
#             nparr = np.frombuffer(image_bytes, np.uint8)
#             image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#             if image is None:
#                 return Response({"error": "Invalid image data"}, status=status.HTTP_400_BAD_REQUEST)

#             # ---------- Step 1: OCR Text Extraction with Tesseract ----------
#             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#             extracted_text = pytesseract.image_to_string(gray)

#             # ---------- Step 2: Extract CNIC Number ----------
#             cnic_match = re.search(r"\d{5}-\d{7}-\d", extracted_text)
#             cnic_number = cnic_match.group(0) if cnic_match else None

#             # ---------- Step 3: Extract Name ----------
#             name = None
#             lines = extracted_text.split("\n")
#             for i, line in enumerate(lines):
#                 if "name" in line.lower():
#                     if i + 1 < len(lines):
#                         name = lines[i + 1].strip()
#                     break

#             # ---------- Step 4: Crop CNIC photo area (unchanged) ----------
#             height, width, _ = image.shape
#             x1, y1 = int(width * 0.7), int(height * 0.25)
#             x2, y2 = int(width * 0.95), int(height * 0.70)
#             face_crop = image[y1:y2, x1:x2]

#             # Encode cropped photo as Base64
#             _, buffer = cv2.imencode(".jpg", face_crop)
#             face_image_b64 = base64.b64encode(buffer).decode("utf-8")

#             return Response({
#                 "extracted_text": extracted_text,
#                 "valid": bool(cnic_number),
#                 "cnic_number": cnic_number,
#                 "name": name,
#                 "face_image": face_image_b64,
#                 "error": None if cnic_number else "CNIC number not found"
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "extracted_text": "",
#                 "valid": False,
#                 "cnic_number": None,
#                 "name": None,
#                 "face_image": None,
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# the most ocrrecct is above code






















































# views.py
import base64
import re
import cv2
import numpy as np
import pytesseract
import face_recognition
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback
import requests

# Set Tesseract path (Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def _b64_to_cv2_img(b64string):
    """Remove header if present and decode base64 to OpenCV BGR image."""
    if not b64string:
        return None
    if "," in b64string:
        b64string = b64string.split(",")[1]
    try:
        img_bytes = base64.b64decode(b64string)
    except Exception:
        return None
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


class CNICVerificationView(APIView):
    """
    Accepts JSON { "image": "data:image/jpeg;base64,..." }
    Uses Tesseract OCR to extract text and crop the CNIC photo area (keeps your crop logic).
    Returns: extracted_text, valid(bool), cnic_number, name, face_image (base64 of crop)
    """
    def post(self, request):
        try:
            image_b64 = request.data.get('image')
            if not image_b64:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

            image = _b64_to_cv2_img(image_b64)
            if image is None:
                return Response({"error": "Invalid image data"}, status=status.HTTP_400_BAD_REQUEST)

            # ---------- OCR with pytesseract ----------
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # small denoise + threshold can improve results; keep minimal to avoid heavy memory
            gray = cv2.medianBlur(gray, 3)
            extracted_text = pytesseract.image_to_string(gray, config='--psm 6')  # single block

            # ---------- CNIC number extraction ----------
            cnic_match = re.search(r"\d{5}-\d{7}-\d", extracted_text)
            cnic_number = cnic_match.group(0) if cnic_match else None

            # ---------- Name extraction ----------
            name = None
            lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
            for i, line in enumerate(lines):
                if 'name' in line.lower():
                    if i + 1 < len(lines):
                        name = lines[i + 1].strip()
                    break

            # ---------- Crop CNIC photo area (UNCHANGED from your logic) ----------
            height, width, _ = image.shape
            x1, y1 = int(width * 0.7), int(height * 0.25)    # top-left corner (right side, lower)
            x2, y2 = int(width * 0.95), int(height * 0.70)   # bottom-right corner
            face_crop = image[y1:y2, x1:x2]

            # If cropping fails (out of bounds) fallback to small center crop
            if face_crop is None or face_crop.size == 0:
                ch, cw = height // 4, width // 4
                face_crop = image[height//2 - ch//2: height//2 + ch//2, width//2 - cw//2: width//2 + cw//2]

            # Encode cropped photo as Base64 (no header)
            _, buffer = cv2.imencode('.jpg', face_crop, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            face_image_b64 = base64.b64encode(buffer).decode('utf-8')

            return Response({
                "extracted_text": extracted_text,
                "valid": bool(cnic_number),
                "cnic_number": cnic_number,
                "name": name,
                "face_image": face_image_b64,   # NOTE: base64 without data: prefix
                "error": None if cnic_number else "CNIC number not found"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "extracted_text": "",
                "valid": False,
                "cnic_number": None,
                "name": None,
                "face_image": None,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    








