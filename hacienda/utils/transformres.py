import base64

def formatmessage(prediales: list) -> str:
    message = ""
    for index, predial in enumerate(prediales):
        message += f'*{index+1}.* {predial.split('-')[1]}DY_SALTO'
    return message

def formatpredial(prediales: list) -> list:
    predial_list_str = ''
    for predial in prediales:
        predial_list_str += f'{predial.split('-')[0]} '
    return predial_list_str

def convertBase64ToPDF(pdfBase64: str, path: str) -> str:
    # Decodificar la cadena Base64
    pdf_bytes = base64.b64decode(pdfBase64)

    # Escribir los bytes en un archivo PDF
    with open(f'{path}', "wb") as pdf_file:
        pdf_file.write(pdf_bytes)
    
    return True