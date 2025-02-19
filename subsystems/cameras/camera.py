from flask import Flask, Response, render_template
import cv2

# Pins for Motor Driver Inputs
MOTOR_PWRA = 1 
MOTOR_DIRA = 21
MOTOR_PWRB = 1
MOTOR_DIRB = 20

app = Flask(__name__)

# Initialize frame number
frameNum = 0

# Example for video capture function
def generate():
    global frameNum
    cap = cv2.VideoCapture(0)  # Replace with your actual video source or Pi camera
    if not cap.isOpened():
        print("Error: Could not open video stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame not captured")
            continue

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        _, buffer = cv2.imencode('.jpg', frame)
        
        frameNum += 1
        print("[SUCCESS] Frame #" + str(frameNum) + " captured successfully")
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def home():
    return render_template("index.html")  # Ensure you have this template

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
