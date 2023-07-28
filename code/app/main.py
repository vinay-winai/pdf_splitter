from fastapi import FastAPI, UploadFile, File 
from pypdf import PdfReader, PdfWriter
from typing import Optional
from fastapi.responses import FileResponse

app = FastAPI()

# # Simulated OAuth2 token verification (Replace with actual OAuth2 verification)
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     if not verify_token(token):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     return token

# def verify_token(token: str) -> bool:
#     # Your OAuth2 token verification logic here (e.g., validate against the OAuth2 provider)
#     # Replace this with the actual verification process
#     # For example, check if the token is valid, hasn't expired, and is associated with a valid user.
#     return True

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def split_pdf_pages(input_file, max_dim_val):
    # File input validation
    try:
        if input_file.content_type not in ['application/pdf', 'application/x-pdf']:
            return "File type is not pdf"
        _15_MB = 15*(1024**2)
        file_size = input_file.file.seek(0,2)
        if file_size > _15_MB:
            return 'File size cannot exceed 15MB'
        pdf = PdfReader(input_file.file)
        if pdf.is_encrypted:
            return 'File is encrypted'
    except Exception as _e:
        print(_e)
        return 'invalid input file'
    #----------------------------------------
    #Page split Algorithm
    writer = PdfWriter()
    for page in pdf.pages:
        _mb = page.mediabox
        width = _mb.width
        # Height split
        while True:
            _mb.bottom = max(_mb.top-max_dim_val,0)    
            #--------------------------------------------------
            if width > max_dim_val:
            # Width split for each height split
                _mb.right = 0
                while True:
                    _mb.right = min(_mb.right+max_dim_val,width)
                    writer.add_page(page)
                    if _mb.left+max_dim_val <= width:
                        _mb.left += max_dim_val
                    else:
                        _mb.left = _mb.right = 0
                        break
            #--------------------------------------------------
            else:writer.add_page(page)
            if _mb.top >= max_dim_val:
                _mb.top -= max_dim_val
            else:break
    with open("output.pdf", 'wb') as file:
        writer.write(file)
    
    return FileResponse('output.pdf', media_type="application/pdf",
            headers = {"Content-Disposition": "attachment; \
                      filename=output.pdf"})

@app.post("/process_pdf/")
async def split_pdf_pages_endpoint(
    input_file: UploadFile = File(...),
    max_dim_val: Optional[int] = 3480,
    # current_user: str = Depends(get_current_user)
):
    return split_pdf_pages(input_file, max_dim_val)