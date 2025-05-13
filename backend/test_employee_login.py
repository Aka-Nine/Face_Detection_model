import requests
import cv2

BASE_URL = "http://127.0.0.1:8000"

def test_employee_login_with_password():
    """Test employee login using email and password."""
    data = {
        "email": "employee2@example.com",
        "password": "securepassword"
    }
    
    response = requests.post(f"{BASE_URL}/login/password", data=data)
    print("Employee Login with Password Response:", response.json())

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

def test_employee_login_with_face():
    """Test employee login using face recognition."""
    image_bytes = capture_image()
    if image_bytes is None:
        print("Failed to capture image.")
        return

    files = {"image": ("employee.jpg", image_bytes, "image/jpeg")}
    response = requests.post(f"{BASE_URL}/login/face/employee", files=files)
    print("Employee Login with Face Response:", response.json())

if __name__ == "__main__":
    test_employee_login_with_password()
    test_employee_login_with_face()
