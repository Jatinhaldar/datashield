from io import BytesIO
import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image

# Configure Tesseract path for Windows
# Make sure to install it to this exact path or update this line if you put it elsewhere!
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_pdf(file_bytes: bytes) -> str:
    text_content = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
    return text_content

def parse_excel(file_bytes: bytes) -> str:
    df = pd.read_excel(BytesIO(file_bytes))
    return df.to_string()

def parse_csv(file_bytes: bytes) -> str:
    df = pd.read_csv(BytesIO(file_bytes))
    return df.to_string()

def parse_image(file_bytes: bytes, lang: str = 'eng') -> str:
    image = Image.open(BytesIO(file_bytes))
    
    # Check if the requested language is installed in Tesseract
    try:
        available_langs = pytesseract.get_languages(config="")
        # Support multiple languages passed as 'eng+hin'
        requested_langs = lang.split('+')
        missing_langs = [l for l in requested_langs if l not in available_langs]
        
        if missing_langs:
            raise ValueError(f"Tesseract language pack(s) missing: {', '.join(missing_langs)}. "
                             f"Please install them in your Tesseract-OCR/tessdata folder.")
                             
        extracted_text = pytesseract.image_to_string(image, lang=lang)
        return extracted_text
    except pytesseract.TesseractNotFoundError:
        raise ValueError("Tesseract-OCR not found. Please check your installation path.")
    except Exception as e:
        if "TESSDATA_PREFIX" in str(e) or "actual_tessdata_num_langs" in str(e):
             raise ValueError(f"Language pack '{lang}' is not installed in Tesseract.")
        raise e

def extract_text_from_file(filename: str, file_bytes: bytes, lang: str = 'eng') -> str:
    if not filename:
        raise ValueError("Filename is required")
        
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return parse_pdf(file_bytes)
    elif ext in ['xlsx', 'xls']:
        return parse_excel(file_bytes)
    elif ext == 'csv':
        return parse_csv(file_bytes)
    elif ext in ['png', 'jpg', 'jpeg', 'bmp']:
        return parse_image(file_bytes, lang)
    elif ext == 'txt':
        return file_bytes.decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file format: {ext}")
