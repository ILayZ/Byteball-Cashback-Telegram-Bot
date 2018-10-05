import io
from google.oauth2 import service_account
	
from CREDENTIALS import VISION_KEY_PATH

credentials = service_account.Credentials.from_service_account_file(
    VISION_KEY_PATH)

client = vision.ImageAnnotatorClient(credentials=credentials)

def read_image(filepath):
    with io.open(filepath, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
	# Language hint codes for handwritten OCR:
    # en-t-i0-handwrit, mul-Latn-t-i0-handwrit
    # Note: Use only one language hint code per request for handwritten OCR.
    image_context = vision.types.ImageContext(language_hints=['ru'])
    response = client.document_text_detection(image=image, image_context=image_context)
    document = response.full_text_annotation.text
    
    if document == '':
        return "Oops, I didn't seem to find anything. Please try again."
    else:
        return document
