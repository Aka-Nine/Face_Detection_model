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

def test_checkout():
    """Test employee check-out using face recognition."""
    image_bytes = capture_image()
    if image_bytes is None:
        print("Failed to capture image.")
        return

    files = {"image": ("checkout.jpg", image_bytes, "image/jpeg")}
    response = requests.post(f"{BASE_URL}/attendance/checkout", files=files)
    print("Check-out Response:", response.json())

if __name__ == "__main__":
    test_checkout()

