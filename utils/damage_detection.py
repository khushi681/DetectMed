import cv2
import os
import numpy as np

def detect_damage(image_path):
    img = cv2.imread(image_path)

    # Convert to grayscale & blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Edge detection (shows foil leakage/dent regions)
    edges = cv2.Canny(blur, 50, 150)

    # Convert edges to 3-channel for concatenation
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # SIDE-BY-SIDE COMPARISON
    combined = np.hstack((img, edges_colored))

    # Save file
    filename = "processed_" + os.path.basename(image_path)
    output_path = os.path.join("processed", filename)

    cv2.imwrite(output_path, combined)

    # Simple damage logic
    white_pixels = cv2.countNonZero(edges)
    if white_pixels > 5000:
        status = "DAMAGED / POSSIBLE LEAK"
    else:
        status = "PACKAGING OK"

    return status, filename


