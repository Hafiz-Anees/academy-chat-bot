import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.whatsapp import send_whatsapp_message

# Replace with YOUR own WhatsApp number in international format, no '+', no spaces
# This must be a number added as a "test recipient" in Meta's console if using a temporary token
TEST_NUMBER = "923430101316"

result = send_whatsapp_message(TEST_NUMBER, "Test message from academy backend")
print(result)