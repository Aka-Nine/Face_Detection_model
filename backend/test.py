import requests
import cv2

BASE_URL = "http://127.0.0.1:8000"

def capture_image():
    """Capture an image using the webcam and return it as bytes."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Error: Could not access the camera")
        return None

    print("📸 Press SPACE to capture the image...")
    while True:
        ret, frame = cam.read()
        cv2.imshow("Capture Image", frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):  # Press SPACE to capture
            break

    cam.release()
    cv2.destroyAllWindows()

    _, img_encoded = cv2.imencode(".jpg", frame)
    return img_encoded.tobytes()

def test_checkin():
    """Test employee check-in using face recognition."""
    image_bytes = capture_image()
    if image_bytes is None:
        print("❌ Failed to capture image.")
        return

    files = {"image": ("checkin.jpg", image_bytes, "image/jpeg")}
    try:
        response = requests.post(f"{BASE_URL}/attendance/checkin", files=files)
        print(f"📡 Status Code: {response.status_code}")

        try:
            json_data = response.json()
            print("✅ Check-in Response (JSON):", json_data)
        except ValueError:
            print("❌ Response is not JSON.")
            print("🔍 Raw Response:", response.text)

    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)

if __name__ == "__main__":
    test_checkin()
