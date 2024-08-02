from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

@api_view(['GET', 'POST'])
def getlocalesbycc(request: Request):
    try:
        pass
    except Exception as e:
        return Response({'mensaje': str(e)}, status=status.HTTP_400_BAD_REQUEST)