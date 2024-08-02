import base64

def formatmessage(prediales: list) -> str:
    emojis = [ '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', '0️⃣']
    message = ""
    for index, predial in enumerate(prediales):
        msj = f'{emojis[index]} {predial.split('-')[1]} \n'
        message += msj + '                                                                                                                            ' #No borrar estos espacios para que se vea como lista en whatsapp.
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