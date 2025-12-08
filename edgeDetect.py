import cv2
import numpy as np

cap = cv2.VideoCapture(0) 

while True:
    ret, frame = cap.read() # Read a frame

    if not ret: # Break the loop if reading frame fails
        break

    # Convert to grayscale (Canny works best on grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150) # Adjust thresholds as needed

    # Display the original and edge-detected frames
    cv2.imshow('Original Frame', frame)
    cv2.imshow('Canny Edges', edges)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()