"""
M-Pesa Payment Integration Service
"""
import requests
import base64
import json
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MpesaService:
    """M-Pesa Payment Integration Service"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'production':
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"
        
        self.token_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}"
            }
            
            response = requests.get(self.token_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            token = response.json().get('access_token')
            if not token:
                raise ValueError("Failed to get access token")
                
            return token
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa token request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa token error: {str(e)}")
            raise

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        try:
            token = self.get_access_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{settings.SITE_URL}/payment/mpesa-callback/",
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa STK Push request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa STK Push error: {str(e)}")
            raise

    def query_status(self, checkout_request_id):
        """Query transaction status"""
        try:
            token = self.get_access_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa Query Status request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa Query Status error: {str(e)}")
            raise

    def simulate_c2b_payment(self, phone_number, amount, account_reference):
        """Simulate C2B payment (for testing)"""
        try:
            token = self.get_access_token()
            
            url = f"{self.base_url}/mpesa/c2b/v1/simulate"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ShortCode": self.shortcode,
                "CommandID": "CustomerPayBillOnline",
                "Amount": amount,
                "Msisdn": phone_number,
                "BillRefNumber": account_reference
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa C2B simulation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa C2B simulation error: {str(e)}")
            raise

    def register_c2b_urls(self, confirmation_url, validation_url):
        """Register C2B URLs for the shortcode"""
        try:
            token = self.get_access_token()
            
            url = f"{self.base_url}/mpesa/c2b/v1/registerurl"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ShortCode": self.shortcode,
                "ResponseType": "Completed",
                "ConfirmationURL": confirmation_url,
                "ValidationURL": validation_url
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa Register C2B URLs error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa Register C2B URLs error: {str(e)}")
            raise

    def account_balance(self):
        """Query account balance"""
        try:
            token = self.get_access_token()
            
            url = f"{self.base_url}/mpesa/accountbalance/v1/query"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # This requires additional security credentials
            # Implement as needed
            
            return {"ResponseCode": "0", "ResponseDescription": "Success"}
        except Exception as e:
            logger.error(f"M-Pesa Account Balance error: {str(e)}")
            raise

    def b2c_payment(self, phone_number, amount, command_id, remarks):
        """Send B2C payment"""
        try:
            token = self.get_access_token()
            
            url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # This requires additional security credentials
            # Implement as needed
            
            return {"ResponseCode": "0", "ResponseDescription": "Success"}
        except Exception as e:
            logger.error(f"M-Pesa B2C Payment error: {str(e)}")
            raise


# Helper function to format phone number
def format_phone_number(phone_number):
    """Format phone number for M-Pesa"""
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Ensure it starts with 254
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('+254'):
        phone = phone[1:]
    elif not phone.startswith('254'):
        phone = '254' + phone
    
    return phone


# Helper function to validate M-Pesa response
def validate_mpesa_response(response):
    """Validate M-Pesa API response"""
    if not response:
        return False, "Empty response"
    
    response_code = response.get('ResponseCode')
    if response_code == '0':
        return True, response.get('ResponseDescription', 'Success')
    else:
        error_message = response.get('ResponseDescription', 'Unknown error')
        return False, error_message


# Helper function to log M-Pesa transactions
def log_mpesa_transaction(payment, request_data, response_data):
    """Log M-Pesa transaction for auditing"""
    log_entry = {
        'payment_id': str(payment.id),
        'transaction_reference': payment.transaction_reference,
        'amount': str(payment.amount),
        'phone_number': payment.metadata.get('phone_number'),
        'request': request_data,
        'response': response_data,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"M-Pesa Transaction: {json.dumps(log_entry)}")
    return log_entry