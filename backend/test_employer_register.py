import requests
import cv2

BASE_URL = "http://127.0.0.1:8000"

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

def test_register_employer():
    """Test employer registration."""
    image_bytes = capture_image()
    if image_bytes is None:
        print("Failed to capture image.")
        return

    files = {"image": ("employer.jpg", image_bytes, "image/jpeg")}
    data = {
        "username": "test_employer",
        "email": "employer6@example.com",
        "password": "securepassword"
    }

    response = requests.post(f"{BASE_URL}/employer/register", data=data, files=files)
    print("Employer Registration Response:", response.json())

if __name__ == "__main__":
    test_register_employer()
