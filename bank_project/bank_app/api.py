from django.http import Http404
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ExternalTransferSerializer
from .models import ExternalTransfer, Ledger, Account, Customer
from .models.external_transfer import TransferStatus

class ExternalTransferList(APIView):
    def get(self, request, format=None):
        transfers = ExternalTransfer.objects.all()
        serializer = ExternalTransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = ExternalTransferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if not ExternalTransfer.objects.filter(idempotency_key=serializer.initial_data['idempotency_key']):
                    serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    def get_object(self, pk):
        try:
            return ExternalTransfer.objects.get(pk=pk)
        except ExternalTransfer.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        external_transfer = self.get_object(pk)
        if external_transfer.status == TransferStatus.COMPLETED:
            return Response(status=status.HTTP_200_OK)
        customer_acc = Account.objects.get(ban=external_transfer.credit_account)
        external_transactions_acc = Customer.external_transactions_acc()
        try:
            Ledger.transfer(
                amount=external_transfer.amount, 
                debit_account=external_transactions_acc, 
                debit_text=external_transfer.text, 
                credit_account=customer_acc,
                credit_text=external_transfer.text,
                external_transfer=True
            )
            external_transfer.status = TransferStatus.COMPLETED
            external_transfer.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExternalTransferFailed(APIView):
    def patch(self, request, pk):
        ...