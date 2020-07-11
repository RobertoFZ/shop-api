import openpay
from shop.settings import OPEN_PAY_SANDBOX_ACTIVE, OPEN_PAY_PRIVATE_KEY, OPEN_PAY_ID, OPEN_PAY_PUBLIC_KEY


class OpenPayManager():
    api_key = OPEN_PAY_PRIVATE_KEY
    merchant_id = OPEN_PAY_ID
    openpay = None

    def __init__(self):
        openpay.api_key = self.api_key
        openpay.merchant_id = self.merchant_id
        openpay.verify_ssl_certs = False

        # Environment
        is_production = False if OPEN_PAY_SANDBOX_ACTIVE in [
            'True', 'true', '1'] else True

        openpay.api_base = 'https://sandbox-api.openpay.mx/v1' if not is_production else 'https://api.openpay.mx/v1'
        openpay.production = is_production
        self.openpay = openpay

    def create_charge(self, charge):
        response = None
        try:
            response = self.openpay.Charge.create_as_merchant(**charge)
        except Exception as error:
            print(error)
            return {'error': True, 'data': str(error)}
        return {'error': False, 'data': response}

    def get_charge(self, charge_id):
        response = None
        try:
            response = self.openpay.Charge.retrieve_as_merchant(charge_id)
        except Exception as error:
            print(error)
        return response
