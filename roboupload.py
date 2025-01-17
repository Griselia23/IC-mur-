import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import torch
import cv2
from PIL import Image, ImageTk
from matplotlib import pyplot as plt

# Load YOLOv5 model (replace the path with your model file)
model = torch.hub.load('ultralytics/yolov5', 'custom', path='path/to/your/model.pt')

# Function to perform object detection on an image
def detect_objects(image_path):
    # Read the image using OpenCV
    img = cv2.imread(image_path)
    
    # Convert the image from BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Perform inference on the image
    results = model(img_rgb)
    
    # Show the results
    results.show()

    # Optionally save the output with bounding boxes
    results.save()  # Saves the image with boxes in 'runs/detect/exp'

    # Display results using Tkinter (as an image in the Tkinter window)
    result_image = Image.fromarray(results.imgs[0])  # Convert result to image
    result_image = result_image.resize((500, 500), Image.ANTIALIAS)  # Resize for display
    result_image = ImageTk.PhotoImage(result_image)

    # Update the label to show the result
    result_label.config(image=result_image)
    result_label.image = result_image  # Keep a reference to the image

# Function to browse and upload an image
def browse_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")])
    
    if file_path:
        try:
            # Read and display the uploaded image
            img = Image.open(file_path)
            img = img.resize((500, 500), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            
            # Update the label to display the uploaded image
            uploaded_image_label.config(image=img)
            uploaded_image_label.image = img  # Keep a reference to the image
            
            # Perform object detection on the uploaded image
            detect_objects(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")

# Set up the Tkinter root window
root = tk.Tk()
root.title("YOLOv5 Object Detection")

# Create a label to display the uploaded image
uploaded_image_label = tk.Label(root)
uploaded_image_label.pack(pady=10)

# Create a button to browse and upload an image
browse_button = tk.Button(root, text="Upload Image", command=browse_image, width=20, height=2)
browse_button.pack(pady=10)

# Create a label to display the result image after object detection
result_label = tk.Label(root)
result_label.pack(pady=10)

# Run the Tkinter event loop
root.mainloop()
