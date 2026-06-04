import cv2
import time
import serial

# ==========================
# FIXED MediaPipe Import
# ==========================
# Direct import method for MediaPipe
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# ==========================
# Connect to ESP32
# ==========================
try:
    # Replace 'COM5' with your ESP32 port
    esp32 = serial.Serial('COM5', 9600)
    time.sleep(2)  # Give ESP32 time to reset and establish connection
    esp32_connected = True
    print("✅ ESP32 connected.")
except Exception as e:
    esp32_connected = False
    print(f"⚠️ ESP32 not connected. Running in demo mode. Error: {e}")

# ==========================
# Initialize MediaPipe Hands
# ==========================
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ==========================
# Initialize video capture
# ==========================
cap = cv2.VideoCapture(0)  # 0 for default webcam
if not cap.isOpened():
    print("Error: Could not open video stream. Check camera connection or index.")
    exit()

# ==========================
# Finger detection logic (keep your existing function)
# ==========================
def get_finger_states(lm_list):
    # Finger tips: Thumb(4), Index(8), Middle(12), Ring(16), Pinky(20)
    finger_tips = [8, 12, 16, 20]
    fingers = []

    # Thumb (open if tip is left of joint for right hand)
    if lm_list[4][0] < lm_list[3][0]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip_id in finger_tips:
        if lm_list[tip_id][1] < lm_list[tip_id - 2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

# ==========================
# Main loop (keep the rest of your code from here)
# ==========================
prev_finger_state_byte = -1  # Initialize with invalid state

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame. Exiting...")
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    current_finger_state_byte = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, _ = img.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            if lm_list:
                fingers = get_finger_states(lm_list)
                print("Fingers (Thumb, Index, Middle, Ring, Pinky):", fingers)

                # Convert finger list to byte
                for i, state in enumerate(fingers):
                    if state == 1:
                        current_finger_state_byte |= (1 << i)

                print(f"Sending byte: {current_finger_state_byte} (Binary: {bin(current_finger_state_byte)})")

                # Send to ESP32 only if state changed
                if esp32_connected and current_finger_state_byte != prev_finger_state_byte:
                    try:
                        esp32.write(bytes([current_finger_state_byte]))
                        prev_finger_state_byte = current_finger_state_byte
                    except serial.SerialException as e:
                        print(f"Error writing to ESP32: {e}")
                        esp32_connected = False
                        print("⚠️ ESP32 connection lost. Please check connection and restart script.")

            # Draw landmarks with updated method
            mp_drawing.draw_landmarks(
                img,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

    cv2.imshow("Robotic Hand Control", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==========================
# Cleanup
# ==========================
cap.release()
cv2.destroyAllWindows()
if esp32_connected:
    esp32.close()
    print("ESP32 serial connection closed.")
print("Script finished.")