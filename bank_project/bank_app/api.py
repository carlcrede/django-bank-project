from django.http import Http404
from django.db import transaction
from rest_framework import status
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
    
    def account_exists(self, acc_pk) -> bool:
        return Account.objects.filter(pk=acc_pk).exists()

    def transfer_exists(self, transfer_pk) -> bool:
        return ExternalTransfer.objects.filter(pk=transfer_pk).exists()

    def post(self, request, format=None):
        serializer = ExternalTransferSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not self.account_exists(acc_pk=serializer.validated_data.get('credit_account')):
            return Response('Unknown account BAN', status=status.HTTP_404_NOT_FOUND)

        if self.transfer_exists(transfer_pk=serializer.validated_data.get('idempotency_key')):
            return Response('Idempotency error', status=status.HTTP_409_CONFLICT)
        
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        customer_acc = Account.objects.get(ban=external_transfer.credit_account)
        external_transactions_acc = Customer.external_transactions_acc()
        try:
            with transaction.atomic():
                Ledger.transfer(
                    amount=external_transfer.amount, 
                    debit_account=external_transactions_acc, 
                    debit_text=external_transfer.text, 
                    credit_account=customer_acc,
                    credit_text=external_transfer.text,
                    external_transfer=True
                )
                external_transfer.status = TransferStatus.CONFIRMED
                external_transfer.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExternalTransferComplete(APIView):
    def get_object(self, pk):
        try:
            return ExternalTransfer.objects.get(pk=pk)
        except ExternalTransfer.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        external_transfer = self.get_object(pk)
        try:
            external_transfer.status = TransferStatus.COMPLETED
            external_transfer.save()
        except Exception as exc:
            return Response(exc, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_200_OK)


class ExternalTransferFailed(APIView):
    def get_object(self, pk):
        try:
            return ExternalTransfer.objects.get(pk=pk)
        except ExternalTransfer.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        external_transfer = self.get_object(pk=pk)
        try:
            if (
                external_transfer.status == TransferStatus.COMPLETED or
                external_transfer.status == TransferStatus.CONFIRMED
            ):
                with transaction.atomic():
                    Ledger.transfer(
                        amount=external_transfer.amount, 
                        debit_account=Account.objects.get(ban=external_transfer.credit_account), 
                        debit_text='external transfer reversal', 
                        credit_account=Customer.external_transactions_acc(),
                        credit_text='external transfer reversal',
                        direct_transaction_with_bank=True
                    )
                    external_transfer.status = TransferStatus.FAILED
                    external_transfer.save()
                return Response(status=status.HTTP_200_OK)
            
            if external_transfer.status == TransferStatus.RESERVED:
                external_transfer.status = TransferStatus.FAILED
                external_transfer.save()
                return Response(status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(exc, status=status.HTTP_500_INTERNAL_SERVER_ERROR)