import requests

base_url = "http://localhost:5000/api"

def test_endpoints():
    try:
        # 1. Test getting chat history
        # Using some mock user_a and user_b values to trigger the DB lookup
        print("Testing GET /chat/history...")
        r = requests.get(f"{base_url}/chat/history?user_a=test_user_1&user_b=test_user_2")
        print("Status:", r.status_code)
        print("Response:", r.json())
        
        # 2. Test sending a universal message
        print("\nTesting POST /chat/send-universal...")
        r2 = requests.post(f"{base_url}/chat/send-universal", json={
            "sender_id": "test_user_1",
            "recipient_id": "test_user_2",
            "sender_name": "Test Sender",
            "sender_role": "patient",
            "recipient_role": "doctor",
            "message": "This is a backend integrity diagnostic message"
        })
        print("Status:", r2.status_code)
        print("Response:", r2.json())
        
        # 3. Test getting chat history again (should contain the message now)
        print("\nRe-Testing GET /chat/history...")
        r3 = requests.get(f"{base_url}/chat/history?user_a=test_user_1&user_b=test_user_2")
        print("Status:", r3.status_code)
        res = r3.json()
        print("Response Success:", res.get("status"))
        print("Message Count:", len(res.get("messages", [])))
        if len(res.get("messages", [])) > 0:
            print("Last Message Content:", res.get("messages")[-1].get("message"))
            
    except Exception as e:
        print("CRITICAL EXCEPTION DURING API DIAGNOSTIC:", str(e))

if __name__ == "__main__":
    test_endpoints()
