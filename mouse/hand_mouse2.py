import cv2
import numpy as np
import pyautogui


# ============================================================
# SETTINGS
# ============================================================

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Smoothing
SMOOTHING = 0.25

# Minimum contour area
MIN_AREA = 5000


# ============================================================
# SCREEN
# ============================================================

screen_width, screen_height = pyautogui.size()

print("Screen:", screen_width, "x", screen_height)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)


# ============================================================
# SMOOTHING VARIABLES
# ============================================================

previous_x = screen_width // 2
previous_y = screen_height // 2


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera error")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape


    # ========================================================
    # HSV
    # ========================================================

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )


    # ========================================================
    # SKIN MASK
    # ========================================================

    lower_skin = np.array([
        0,
        20,
        70
    ])

    upper_skin = np.array([
        25,
        255,
        255
    ])

    mask = cv2.inRange(
        hsv,
        lower_skin,
        upper_skin
    )


    # ========================================================
    # MORPHOLOGICAL OPERATIONS
    # ========================================================

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )


    # ========================================================
    # FIND CONTOURS
    # ========================================================

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )


    if contours:

        # Largest contour
        hand = max(
            contours,
            key=cv2.contourArea
        )

        area = cv2.contourArea(hand)


        if area > MIN_AREA:

            # =================================================
            # DRAW HAND
            # =================================================

            cv2.drawContours(
                frame,
                [hand],
                -1,
                (0, 255, 0),
                2
            )


            # =================================================
            # FIND TOPMOST POINT
            # =================================================

            top_index = hand[:, :, 1].argmin()

            top_point = tuple(
                hand[top_index][0]
            )

            x, y = top_point


            # Draw fingertip candidate
            cv2.circle(
                frame,
                (x, y),
                12,
                (0, 0, 255),
                -1
            )


            # =================================================
            # CAMERA → SCREEN
            # =================================================

            target_x = int(
                x / width * screen_width
            )

            target_y = int(
                y / height * screen_height
            )


            # =================================================
            # SMOOTHING
            # =================================================

            current_x = (
                previous_x * (1 - SMOOTHING)
                +
                target_x * SMOOTHING
            )

            current_y = (
                previous_y * (1 - SMOOTHING)
                +
                target_y * SMOOTHING
            )


            previous_x = current_x
            previous_y = current_y


            # =================================================
            # MOVE REAL MOUSE
            # =================================================

            pyautogui.moveTo(
                int(current_x),
                int(current_y)
            )


            # =================================================
            # DISPLAY COORDINATES
            # =================================================

            cv2.putText(
                frame,
                f"Camera: {x}, {y}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Mouse: {int(current_x)}, {int(current_y)}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    else:

        cv2.putText(
            frame,
            "HAND NOT DETECTED",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Hand Mouse",
        frame
    )

    cv2.imshow(
        "Mask",
        mask
    )


    # ========================================================
    # ESC
    # ========================================================

    if cv2.waitKey(1) & 0xFF == 27:
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()
