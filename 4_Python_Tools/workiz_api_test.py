import requests
import json

# ==============================================================================
# 1. CONFIGURATION - All your data is here. No edits needed.
# ==============================================================================

# Your API credentials
API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
API_SECRET = "sec_334084295850678330105471548"

# The phone number where the test message will be sent
RECIPIENT_PHONE_NUMBER = "9519726946"

# The message we are sending
TEST_MESSAGE = "This is a test of the Workiz API from the Python script. If you receive this, it worked!"

# Workiz API endpoint - Testing with a known working endpoint first
# Let's try getting jobs to verify authentication works
API_ENDPOINT_URL = f"https://api.workiz.com/api/v1/job"

# Note: SMS sending may require a different endpoint or may not be available via API
# Common Workiz endpoints: /job, /client, /lead, /team


# ==============================================================================
# 2. CONSTRUCT THE API REQUEST
# ==============================================================================

# Headers with authentication
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Payload with auth_secret and message details
payload = {
    "auth_secret": API_SECRET,
    "to": RECIPIENT_PHONE_NUMBER,
    "phone": RECIPIENT_PHONE_NUMBER,
    "message": TEST_MESSAGE,
    "body": TEST_MESSAGE
}


# ==============================================================================
# 3. SEND THE REQUEST AND GET THE RESPONSE
# ==============================================================================

print(f"Attempting to send a POST request to: {API_ENDPOINT_URL}")
print("-" * 50)
print(f"Payload being sent:\n{json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    # Test with GET request first to verify authentication
    print("\nFirst, testing authentication with a GET request...")
    response = requests.get(API_ENDPOINT_URL, headers=headers)

    # Print the results for debugging
    print("Request sent! Here is the server's response:")
    print("-" * 50)
    print(f"Status Code: {response.status_code}")
    print("-" * 50)
    
    # Try to print the JSON response, if it exists
    try:
        print("Server Response Body:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Server Response Body (not JSON):")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")