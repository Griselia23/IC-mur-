import os
import sys
import cv2
import time
import numpy as np
from ultralytics import YOLO

# Define the arguments directly in the script
model_path = 'C:\\mur\\my_model\\train\\weights\\best.pt'  # Path to your model
min_thresh = 0.5  # Minimum confidence threshold
user_res = None  # Resolution (None if you don't want to resize)
record = False  # Whether or not to record video output

# Check if model file exists and is valid
if not os.path.exists(model_path):
    print('WARNING: Model path is invalid or model was not found. Using default yolov8s.pt model instead.')
    model_path = 'yolov8s.pt'

# Load the model into memory and get label map
model = YOLO(model_path, task='detect')
labels = model.names

# Set the camera index (0 for the default camera, or 1, 2 for other connected cameras)
camera_index = 0  # Change this if you want to use another camera
cap = cv2.VideoCapture(camera_index)

# Check if camera opened successfully
if not cap.isOpened():
    print(f"Error: Camera {camera_index} could not be opened.")
    sys.exit(0)

# Set resolution if user specified (optional)
if user_res:
    resW, resH = int(user_res.split('x')[0]), int(user_res.split('x')[1])
    cap.set(3, resW)  # Set width
    cap.set(4, resH)  # Set height

# Set bounding box colors
bbox_colors = [(164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133), (88, 159, 106),
               (96, 202, 231), (159, 124, 168), (169, 162, 241), (98, 118, 150), (172, 176, 184)]

# Initialize control and status variables
avg_frame_rate = 0
frame_rate_buffer = []
fps_avg_len = 200

# Begin inference loop
while True:
    t_start = time.perf_counter()

    # Grab a frame from the camera
    ret, frame = cap.read()
    if not ret:
        print('Error: Failed to grab frame from camera.')
        break

    # Resize frame to desired display resolution if specified
    if user_res:
        frame = cv2.resize(frame, (resW, resH))

    # Run inference on the frame
    results = model(frame, verbose=False)

    # Extract results
    detections = results[0].boxes

    # Initialize variable for basic object counting example
    object_count = 0

    # Go through each detection and get bbox coords, confidence, and class
    for i in range(len(detections)):
        xyxy_tensor = detections[i].xyxy.cpu()
        xyxy = xyxy_tensor.numpy().squeeze()
        xmin, ymin, xmax, ymax = xyxy.astype(int)

        classidx = int(detections[i].cls.item())
        classname = labels[classidx]

        conf = detections[i].conf.item()

        if conf > min_thresh:  # Use the minimum threshold for confidence
            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

            label = f'{classname}: {int(conf * 100)}%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            label_ymin = max(ymin, labelSize[1] + 10)
            cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10),
                          (xmin + labelSize[0], label_ymin + baseLine - 10), color, cv2.FILLED)
            cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            object_count += 1

    # Display the results
    cv2.putText(frame, f'Objects detected: {object_count}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow('YOLO Detection - Press q to exit', frame)

    # Wait for the user to press 'q' to quit
    key = cv2.waitKey(1)  # Wait for 1ms to process the next frame
    if key == ord('q') or key == ord('Q'):
        break

    # Calculate FPS
    t_stop = time.perf_counter()
    frame_rate_calc = float(1 / (t_stop - t_start))

    # Append FPS result to frame_rate_buffer (for calculating average FPS)
    if len(frame_rate_buffer) >= fps_avg_len:
        temp = frame_rate_buffer.pop(0)
        frame_rate_buffer.append(frame_rate_calc)
    else:
        frame_rate_buffer.append(frame_rate_calc)

    avg_frame_rate = np.mean(frame_rate_buffer)

# Cleanup
print(f'Average FPS: {avg_frame_rate:.2f}')
cap.release()
cv2.destroyAllWindows()
