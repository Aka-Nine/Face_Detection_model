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

    if frame is None:
        print("❌ Error: No frame captured.")
        return None

    _, img_encoded = cv2.imencode(".jpg", frame)

    if img_encoded is None:
        print("❌ Error: Image encoding failed.")
        return None

    return img_encoded.tobytes()

def test_employer_face_login():
    """Test employer login using face recognition."""
    image_bytes = capture_image()
    
    if image_bytes is None:
        print("⚠️ No image captured. Exiting...")
        return

    files = {"image": ("employer.jpg", image_bytes, "image/jpeg")}
    
    try:
        response = requests.post(f"{BASE_URL}/login/face/employer", files=files)
        response.raise_for_status()  # Raise error for bad responses (4xx, 5xx)
        
        print("✅ Employer Face Login Response:", response.json())

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Failed to send request. {str(e)}")

if __name__ == "__main__":
    test_employer_face_login()
