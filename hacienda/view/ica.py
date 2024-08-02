from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from hacienda.helpers.tnsrequest import TNSRequest
from hacienda.utils.icatransform import getmessage

tns = TNSRequest()


@api_view(['GET', 'POST'])
def getlocalesbycc(request: Request):
    try:
        cc = request.query_params.get('cc')

        if cc is None:
            return Response({'mensaje': 'El número de documento es requerido para realizar la consulta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        tnsresponse = tns.getlocalesbycc(cc=cc)

        message = getmessage(establecimientos=tnsresponse)
        return Response({'mensaje': message}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)