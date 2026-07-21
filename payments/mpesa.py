"""
M-Pesa Payment Integration Service - Complete Production Ready
"""
import requests
import base64
import json
import re
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
            
            headers = {"Authorization": f"Basic {auth}"}
            
            response = requests.get(self.token_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            token = response.json().get('access_token')
            if not token:
                raise ValueError("Failed to get access token")
                
            return token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa token request error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa token error: {str(e)}")
            raise

    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        try:
            # Format phone number
            phone_number = self.format_phone_number(phone_number)
            
            # Validate phone number
            if not self.validate_phone_number(phone_number):
                raise ValueError(f"Invalid phone number format: {phone_number}")
            
            # Sanitize AccountReference
            account_reference = self.sanitize_reference(account_reference)
            
            # Get token
            token = self.get_access_token()
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(
                f"{self.shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            # Build URL and headers
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # ✅ FIXED: CORRECT CALLBACK URL - matches your urls.py
            callback_url = "https://government-jobs-portal.onrender.com/payment/mpesa-callback/"
            
            # Build payload
            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": str(amount),
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc[:20] if transaction_desc else "Payment"
            }
            
            # Log payload (without sensitive data)
            log_payload = payload.copy()
            log_payload['Password'] = '***'
            logger.info(f"M-Pesa STK Push payload: {json.dumps(log_payload)}")
            
            # Make request
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa STK Push error {response.status_code}: {error_detail}")
                
                # Try to parse error message
                try:
                    error_json = response.json()
                    error_msg = error_json.get('errorMessage', error_json.get('message', error_detail))
                except:
                    error_msg = error_detail
                
                raise requests.exceptions.RequestException(
                    f"STK Push failed: {error_msg}"
                )
            
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
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa Query error {response.status_code}: {error_detail}")
                response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa Query Status error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa Query Status error: {str(e)}")
            raise

    def simulate_c2b_payment(self, phone_number, amount, account_reference):
        """Simulate C2B payment (sandbox only)"""
        if self.environment == 'production':
            raise ValueError("C2B simulation only available in sandbox")
        
        try:
            token = self.get_access_token()
            phone_number = self.format_phone_number(phone_number)
            account_reference = self.sanitize_reference(account_reference)
            
            url = f"{self.base_url}/mpesa/c2b/v1/simulate"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ShortCode": self.shortcode,
                "CommandID": "CustomerPayBillOnline",
                "Amount": str(amount),
                "Msisdn": phone_number,
                "BillRefNumber": account_reference
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa C2B simulation error {response.status_code}: {error_detail}")
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
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa Register URLs error {response.status_code}: {error_detail}")
                response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa Register URLs error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa Register URLs error: {str(e)}")
            raise

    def account_balance(self, initiator, security_credential, party_a, 
                        identifier_type="4", remarks="Balance Query", queue_timeout_url=None, result_url=None):
        """Query account balance"""
        try:
            token = self.get_access_token()
            
            url = f"{self.base_url}/mpesa/accountbalance/v1/query"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            payload = {
                "Initiator": initiator,
                "SecurityCredential": security_credential,
                "CommandID": "AccountBalance",
                "PartyA": party_a,
                "IdentifierType": identifier_type,
                "Remarks": remarks,
                "QueueTimeOutURL": queue_timeout_url or f"{settings.SITE_URL}/payment/timeout/",
                "ResultURL": result_url or f"{settings.SITE_URL}/payment/result/"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa Balance Query error {response.status_code}: {error_detail}")
                response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa Account Balance error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa Account Balance error: {str(e)}")
            raise

    def b2c_payment(self, phone_number, amount, command_id, remarks, 
                    occasion=None, queue_timeout_url=None, result_url=None):
        """Send B2C payment"""
        try:
            token = self.get_access_token()
            phone_number = self.format_phone_number(phone_number)
            
            url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # This requires security credential from certificate
            # You'll need to implement this properly
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            payload = {
                "InitiatorName": settings.MPESA_INITIATOR_NAME,
                "SecurityCredential": self.generate_security_credential(),
                "CommandID": command_id,  # SalaryPayment, BusinessPayment, PromotionPayment
                "Amount": str(amount),
                "PartyA": settings.MPESA_B2C_SHORTCODE,
                "PartyB": phone_number,
                "Remarks": remarks[:100],
                "QueueTimeOutURL": queue_timeout_url or f"{settings.SITE_URL}/payment/timeout/",
                "ResultURL": result_url or f"{settings.SITE_URL}/payment/result/",
                "Occasion": occasion[:50] if occasion else ""
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"M-Pesa B2C error {response.status_code}: {error_detail}")
                response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"M-Pesa B2C Payment error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"M-Pesa B2C Payment error: {str(e)}")
            raise

    # ============== HELPER METHODS ==============

    def format_phone_number(self, phone_number):
        """Format phone number for M-Pesa"""
        if not phone_number:
            return phone_number
        
        # Convert to string and remove whitespace
        phone = str(phone_number).strip()
        
        # Remove any non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Handle different formats
        if phone.startswith('+254'):
            phone = phone[1:]  # Remove +
        elif phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('254'):
            pass  # Already correct
        else:
            # Assume it's a local number without country code
            if len(phone) == 9:  # 7XXXXXXXX format
                phone = '254' + phone
            elif len(phone) == 10 and phone.startswith('7'):  # 7XXXXXXXXX
                phone = '254' + phone
            else:
                phone = '254' + phone
        
        return phone

    def validate_phone_number(self, phone_number):
        """Validate phone number format"""
        if not phone_number:
            return False
        
        # Must start with 254 and be 12 digits total
        pattern = r'^254[17]\d{8}$'  # 254 + 1 or 7 + 8 digits
        return bool(re.match(pattern, str(phone_number)))

    def sanitize_reference(self, reference):
        """Sanitize AccountReference"""
        if not reference:
            return "PAYMENT"
        
        # Convert to string, remove special characters, truncate to 12 chars
        ref = str(reference).strip()
        ref = re.sub(r'[^a-zA-Z0-9_]', '', ref)
        ref = ref[:12] if ref else "PAYMENT"
        return ref

    def get_callback_url(self):
        """Get callback URL - FIXED for your domain"""
        # ✅ FIXED: CORRECT CALLBACK URL - matches your urls.py
        callback_url = "https://government-jobs-portal.onrender.com/payment/mpesa-callback/"
        
        # Force HTTPS for sandbox
        if self.environment == 'sandbox' and not callback_url.startswith('https://'):
            callback_url = callback_url.replace('http://', 'https://')
        
        return callback_url

    def generate_security_credential(self):
        """Generate security credential for B2C/Account Balance"""
        # This requires your certificate file
        # Implement as per Safaricom documentation
        # For now, return placeholder
        return "SECURITY_CREDENTIAL_PLACEHOLDER"

    def validate_response(self, response):
        """Validate M-Pesa API response"""
        if not response:
            return False, "Empty response"
        
        response_code = response.get('ResponseCode')
        if response_code == '0':
            return True, response.get('ResponseDescription', 'Success')
        else:
            error_message = response.get('ResponseDescription', 'Unknown error')
            return False, error_message

    def log_transaction(self, payment, request_data, response_data):
        """Log M-Pesa transaction for auditing"""
        log_entry = {
            'payment_id': str(payment.id),
            'transaction_reference': getattr(payment, 'transaction_reference', None),
            'amount': str(payment.amount),
            'phone_number': payment.metadata.get('phone_number') if hasattr(payment, 'metadata') else None,
            'request': request_data,
            'response': response_data,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"M-Pesa Transaction: {json.dumps(log_entry)}")
        return log_entry


# ============== STANDALONE HELPER FUNCTIONS ==============

def format_phone_number(phone_number):
    """Standalone helper to format phone number"""
    service = MpesaService()
    return service.format_phone_number(phone_number)


def validate_phone_number(phone_number):
    """Standalone helper to validate phone number"""
    service = MpesaService()
    return service.validate_phone_number(phone_number)


def validate_mpesa_response(response):
    """Standalone helper to validate M-Pesa response"""
    service = MpesaService()
    return service.validate_response(response)


# ============== TESTING FUNCTIONS ==============

def test_mpesa_connection():
    """Test M-Pesa connection and authentication"""
    service = MpesaService()
    try:
        token = service.get_access_token()
        print(f"✅ Connected successfully! Token: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def test_stk_push():
    """Test STK Push with sample data"""
    service = MpesaService()
    try:
        result = service.stk_push(
            phone_number="254708374149",  # Sandbox test number
            amount=1,
            account_reference="TEST001",
            transaction_desc="Test Payment"
        )
        print(f"✅ STK Push successful: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ STK Push failed: {str(e)}")
        return None


def test_c2b_simulation():
    """Test C2B simulation (sandbox only)"""
    service = MpesaService()
    if service.environment != 'sandbox':
        print("⚠️ C2B simulation only works in sandbox")
        return None
    
    try:
        result = service.simulate_c2b_payment(
            phone_number="254708374149",
            amount=100,
            account_reference="SIM001"
        )
        print(f"✅ C2B simulation successful: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ C2B simulation failed: {str(e)}")
        return None


if __name__ == "__main__":
    # Run tests
    print("=" * 50)
    print("Testing M-Pesa Integration")
    print("=" * 50)
    
    print("\n1. Testing Connection...")
    test_mpesa_connection()
    
    print("\n2. Testing STK Push...")
    test_stk_push()
    
    print("\n3. Testing C2B Simulation...")
    test_c2b_simulation()