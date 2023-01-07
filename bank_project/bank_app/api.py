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
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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
        t = self.get_object(pk)
        customer_acc = Account.objects.get(ban=t.credit_account)
        external_transactions_acc = Customer.external_transactions_acc()
        bank_acc = Customer.default_bank_acc()
        try:
            with transaction.atomic():
                Ledger.transfer(t.amount, external_transactions_acc, t.text, bank_acc, t.text, direct_transaction_with_bank=True)
                Ledger.transfer(t.amount, bank_acc, t.text, customer_acc, t.text)
                t.status = TransferStatus.COMPLETED
                t.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)