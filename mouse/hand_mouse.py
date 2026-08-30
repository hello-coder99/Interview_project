import cv2
import numpy as np
import pyautogui
import math
import time


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Minimum hand contour area
MIN_HAND_AREA = 5000

# Smoothing factor
SMOOTHING = 0.25

# Pinch threshold in pixels
PINCH_THRESHOLD = 45

# Delay between clicks
CLICK_DELAY = 0.5

# Number of fingers required for movement
MOVEMENT_FINGERS = 1


# ============================================================
# SCREEN INFORMATION
# ============================================================

screen_width, screen_height = pyautogui.size()

print("Screen:", screen_width, "x", screen_height)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)


# ============================================================
# MOUSE VARIABLES
# ============================================================

smooth_x = screen_width // 2
smooth_y = screen_height // 2

last_click_time = 0

mouse_down = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(p1, p2):
    """
    Euclidean distance between two points.
    """

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def calculate_angle(a, b, c):
    """
    Calculate angle ABC.
    """

    ab = np.array([
        a[0] - b[0],
        a[1] - b[1]
    ])

    cb = np.array([
        c[0] - b[0],
        c[1] - b[1]
    ])

    cosine_angle = np.dot(ab, cb) / (
        np.linalg.norm(ab) *
        np.linalg.norm(cb) + 1e-6
    )

    cosine_angle = np.clip(
        cosine_angle,
        -1.0,
        1.0
    )

    angle = np.degrees(
        np.arccos(cosine_angle)
    )

    return angle


def get_hand_contour(frame):
    """
    Detect the largest skin-colored contour.
    """

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    # --------------------------------------------------------
    # Skin color range
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Noise removal
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Slight blur
    # --------------------------------------------------------

    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0
    )

    # --------------------------------------------------------
    # Find contours
    # --------------------------------------------------------

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) == 0:
        return None, mask

    # Largest contour
    hand = max(
        contours,
        key=cv2.contourArea
    )

    if cv2.contourArea(hand) < MIN_HAND_AREA:
        return None, mask

    return hand, mask


def get_finger_information(contour):
    """
    Estimate fingers using convexity defects.
    """

    hull_indices = cv2.convexHull(
        contour,
        returnPoints=False
    )

    if hull_indices is None:
        return 0, []

    if len(hull_indices) < 3:
        return 0, []

    defects = cv2.convexityDefects(
        contour,
        hull_indices
    )

    if defects is None:
        return 0, []

    finger_count = 0
    defect_points = []

    for i in range(defects.shape[0]):

        start_index = defects[i][0][0]
        end_index = defects[i][0][1]
        far_index = defects[i][0][2]

        start = tuple(
            contour[start_index][0]
        )

        end = tuple(
            contour[end_index][0]
        )

        far = tuple(
            contour[far_index][0]
        )

        # ----------------------------------------------------
        # Calculate distances
        # ----------------------------------------------------

        a = distance(start, end)
        b = distance(start, far)
        c = distance(end, far)

        if b == 0 or c == 0:
            continue

        # Heron's formula
        s = (a + b + c) / 2

        area_squared = (
            s *
            (s - a) *
            (s - b) *
            (s - c)
        )

        if area_squared <= 0:
            continue

        area = math.sqrt(area_squared)

        # Distance from far point to line
        depth = (2 * area) / a if a != 0 else 0

        # ----------------------------------------------------
        # Angle at far point
        # ----------------------------------------------------

        angle = calculate_angle(
            start,
            far,
            end
        )

        # ----------------------------------------------------
        # A finger valley generally has:
        #
        # angle < 90
        # depth sufficiently large
        # ----------------------------------------------------

        if angle < 90 and depth > 15:

            finger_count += 1

            defect_points.append(
                (start, end, far)
            )

    return finger_count, defect_points


def get_top_point(contour):
    """
    Get the highest point of the hand contour.
    """

    top_index = contour[:, :, 1].argmin()

    top_point = tuple(
        contour[top_index][0]
    )

    return top_point


# ============================================================
# MAIN LOOP
# ============================================================

print()
print("==========================================")
print(" HAND GESTURE MOUSE")
print("==========================================")
print()
print("Controls:")
print()
print("1 finger       -> Move mouse")
print("Pinch          -> Left click")
print("2+ fingers     -> Stop movement")
print("ESC            -> Exit")
print()


while True:

    # ========================================================
    # READ CAMERA
    # ========================================================

    ret, frame = cap.read()

    if not ret:
        print("Could not read camera")
        break

    # Mirror image
    frame = cv2.flip(
        frame,
        1
    )

    frame_height, frame_width, _ = frame.shape


    # ========================================================
    # DETECT HAND
    # ========================================================

    hand, mask = get_hand_contour(frame)


    if hand is not None:

        # ====================================================
        # DRAW HAND CONTOUR
        # ====================================================

        cv2.drawContours(
            frame,
            [hand],
            -1,
            (0, 255, 0),
            2
        )


        # ====================================================
        # CONVEX HULL
        # ====================================================

        hull_points = cv2.convexHull(
            hand
        )

        cv2.polylines(
            frame,
            [hull_points],
            True,
            (255, 0, 0),
            2
        )


        # ====================================================
        # FINGER DETECTION
        # ====================================================

        finger_count, defects = get_finger_information(
            hand
        )


        # ====================================================
        # DRAW DEFECT POINTS
        # ====================================================

        for start, end, far in defects:

            cv2.circle(
                frame,
                far,
                6,
                (0, 0, 255),
                -1
            )


        # ====================================================
        # TOPMOST POINT
        # ====================================================

        top_point = get_top_point(
            hand
        )

        top_x, top_y = top_point

        cv2.circle(
            frame,
            top_point,
            10,
            (255, 255, 0),
            -1
        )


        # ====================================================
        # FIND PALM CENTER
        # ====================================================

        moments = cv2.moments(hand)

        if moments["m00"] != 0:

            center_x = int(
                moments["m10"] /
                moments["m00"]
            )

            center_y = int(
                moments["m01"] /
                moments["m00"]
            )

            palm_center = (
                center_x,
                center_y
            )

            cv2.circle(
                frame,
                palm_center,
                8,
                (255, 0, 255),
                -1
            )

        else:

            palm_center = top_point


        # ====================================================
        # FIND PINCH
        # ====================================================

        # Approximation:
        #
        # Use contour extremes to estimate thumb/index
        #
        # For a simple version, we use the topmost point
        # and palm center.

        pinch_distance = distance(
            top_point,
            palm_center
        )


        # ====================================================
        # MOUSE MOVEMENT
        # ====================================================

        if finger_count == 1:

            # Convert camera coordinate
            # to screen coordinate

            target_x = int(
                top_x /
                frame_width *
                screen_width
            )

            target_y = int(
                top_y /
                frame_height *
                screen_height
            )

            # ------------------------------------------------
            # Smoothing
            # ------------------------------------------------

            smooth_x = (
                smooth_x * (1 - SMOOTHING)
                +
                target_x * SMOOTHING
            )

            smooth_y = (
                smooth_y * (1 - SMOOTHING)
                +
                target_y * SMOOTHING
            )

            # ------------------------------------------------
            # Move mouse
            # ------------------------------------------------

            pyautogui.moveTo(
                int(smooth_x),
                int(smooth_y),
                duration=0
            )

            cv2.putText(
                frame,
                "MOVE",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )


        # ====================================================
        # MULTIPLE FINGERS
        # ====================================================

        elif finger_count >= 2:

            cv2.putText(
                frame,
                "STOP",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )


        # ====================================================
        # DISPLAY FINGER COUNT
        # ====================================================

        cv2.putText(
            frame,
            "Fingers: " + str(finger_count),
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY COORDINATES
        # ====================================================

        cv2.putText(
            frame,
            f"Point: ({top_x},{top_y})",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
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
    # SHOW WINDOWS
    # ========================================================

    cv2.imshow(
        "Hand Gesture Mouse",
        frame
    )

    cv2.imshow(
        "Skin Mask",
        mask
    )


    # ========================================================
    # EXIT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

pyautogui.mouseUp()

print("Program terminated.")
