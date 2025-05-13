import requests
import cv2

BASE_URL = "http://127.0.0.1:8000"

def get_employer_token():
    """Get the employer token using email/password login."""
    data = {"email": "employer@example.com", "password": "securepassword"}
    response = requests.post(f"{BASE_URL}/login/password", data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("❌ Employer Login Failed:", response.json())
        return None

def capture_image():
    """Capture an image using the webcam and return it as bytes."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not access the camera")
        return None

    print("Press SPACE to capture the image...")
    while True:
        ret, frame = cam.read()
        cv2.imshow("Capture Image", frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):  # Press SPACE to capture
            break

    cam.release()
    cv2.destroyAllWindows()

    _, img_encoded = cv2.imencode(".jpg", frame)
    return img_encoded.tobytes()

def test_register_employee():
    """Test employee registration with employer authentication."""
    token = get_employer_token()
    if not token:
        print("❌ Could not obtain employer token. Registration failed.")
        return

    image_bytes = capture_image()
    if image_bytes is None:
        print("❌ Failed to capture image.")
        return

    files = {"image": ("employee.jpg", image_bytes, "image/jpeg")}
    data = {
        "employer_id": "67dd58a5ea6247fbf408671d",  # Replace with actual employer ID from the database
        "email": "employee2@example.com",
        "username": "Test Employee",
        "password": "securepassword",
        "hourly_rate": "15.0"
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/employee/register", data=data, files=files, headers=headers)
    print("Employee Registration Response:", response.json())

if __name__ == "__main__":
    test_register_employee()
