import requests
import json
import datetime

# ==============================================================================
# 1. CONFIGURATION - All your data is here. No edits needed.
# ==============================================================================

# Your API credentials
API_TOKEN = "api_1hu6lroiy5zxomcpptuwsg8heju97iwg"
API_SECRET = "sec_334084295850678330105471548"

# The specific Job we are targeting
TARGET_JOB_UUID = "G0M90B"

# The message we will attempt to write to the custom field.
# It includes a timestamp to ensure we can see the result of this specific test run.
TEST_PAYLOAD_MESSAGE = f"API Custom Field Test successful on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# The documented endpoint for updating a job
API_ENDPOINT_URL = f"https://api.workiz.com/api/v1/{API_TOKEN}/job/update/"


# ==============================================================================
# 2. CONSTRUCT THE API REQUEST PAYLOAD
# ==============================================================================

# This is the data we will send to Workiz.
# It identifies the job by its UUID and provides the new text for the target field.
payload = {
    "auth_secret": API_SECRET,
    "UUID": TARGET_JOB_UUID,
    "information_to_remember": TEST_PAYLOAD_MESSAGE
}


# ==============================================================================
# 3. SEND THE REQUEST AND REPORT THE RESPONSE
# ==============================================================================

print(f"Attempting to POST an update to Job UUID: {TARGET_JOB_UUID}")
print(f"Endpoint URL: {API_ENDPOINT_URL}")
print("-" * 50)
print(f"Payload being sent:\n{json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    # We make the API call to the /job/update/ endpoint
    response = requests.post(API_ENDPOINT_URL, json=payload)

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