import cv2

def test_camera(camera_index=0):
    # Open the camera
    cap = cv2.VideoCapture(camera_index)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("[ERROR] Camera is not active or not connected.")
        return False

    # Try to capture a frame
    ret, frame = cap.read()

    # Check if frame was captured
    if not ret:
        print("[ERROR] Failed to capture frame.")
        cap.release()
        return False

    # If successful, display the frame
    print("[SUCCESS] Camera is active, showing a preview frame.")
    cv2.imshow("Camera Test", frame)

    # Wait for a key press and then release the camera
    cv2.waitKey(0)
    cap.release()
    cv2.destroyAllWindows()

    return True

# Test the camera
test_camera()
