from pdf2image import convert_from_bytes

def convert_pdf_to_images(file,poppler_path):
    images = convert_from_bytes(
    file.read(),
    poppler_path=poppler_path
    
)
    return images
