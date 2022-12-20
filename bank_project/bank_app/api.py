from django.http import Http404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ExternalTransferSerializer
from .models import ExternalTransfer

class ExternalTransferList(APIView):
    def get(self, request, format=None):
        transfers = ExternalTransfer.objects.all()
        serializer = ExternalTransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = ExternalTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExternalTransferDetail(APIView):
    def get_object(self, pk):
        try:
            return ExternalTransfer.objects.get(pk=pk)
        except ExternalTransfer.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        transfer = self.get_object(pk)
        serializer = ExternalTransferSerializer(transfer)
        return Response(serializer.data)

class ExternalTransferConfirm(APIView):
    def get():
        ...
    def put():
        ...