import kronos
import httpx
from .models import ExternalTransfer, TransferStatus
import os



@kronos.register('* * * * *')
def confirm_reservation():
    reserved_transfers = ExternalTransfer.objects.filter(status=TransferStatus.RESERVED, from_bank=os.getenv('BANK_REGISTRATION_NUMBER'))
    for t in reserved_transfers:
        try:
            response = httpx.get(f'http://localhost:{t.to_bank}/api/v1/bank/confirm')
            response.raise_for_status()
        except httpx.RequestError as exc:
            print(f'Error while requesting {exc.request.url!r}')
        except httpx.HTTPError as exc:
            print(f'Error response {exc.response.status_code} while requesting {exc.request.url!r}')

def complete():
    ...