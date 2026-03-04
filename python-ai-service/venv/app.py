# Import YOLO model from ultralytics
from ultralytics import YOLO
import cv2

# Load pretrained YOLOv8 model (trained on COCO dataset)
# This loads once when server starts
model = YOLO("yolov8n.pt")

from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil
import os
import time

# Create FastAPI app
app = FastAPI()

# Folder where uploaded and processed images will be stored
UPLOAD_FOLDER = "temp_uploads"

# Create folder if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allow browser/frontend to access images inside temp_uploads
# Example: http://localhost:8000/images/filename.jpg
app.mount("/images", StaticFiles(directory=UPLOAD_FOLDER), name="images")


# Main API endpoint used by backend
@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image.file.close()

        print(f"[AI SERVICE] Image received: {file_path}")

        # Read image using OpenCV
        img = cv2.imread(file_path)

        # Safety check if image cannot be loaded
        if img is None:
            raise Exception("Invalid image file")

        # Run YOLO detection
        results = model(img)

        # Counter for detected persons
        person_count = 0

        # Loop through detection results
        for result in results:
            for box in result.boxes:

                cls = int(box.cls[0])     # class id
                conf = float(box.conf[0]) # confidence score

                # Detect only persons (COCO class id = 0)
                # Also filter weak detections
                if cls == 0 and conf > 0.5:
                    person_count += 1

                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Draw bounding box
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)

                    # Add label text
                    label = f"Person {conf:.2f}"
                    cv2.putText(
                        img,
                        label,
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0,255,0),
                        2
                    )

        # Save annotated image with timestamp to avoid overwriting
        output_filename = f"annotated_{int(time.time())}_{image.filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        cv2.imwrite(output_path, img)

        print(f"[AI SERVICE] Annotated image saved: {output_path}")
        print(f"[AI SERVICE] Persons detected: {person_count}")

        # Generate description text
        if person_count == 0:
            description = "No person detected in the image."
        elif person_count == 1:
            description = "1 person detected in the image."
        else:
            description = f"{person_count} persons detected in the image."

        # Remove original uploaded image to save space
        os.remove(file_path)

        # Return description + annotated image URL
        return {
            "description": description,
            "image_url": f"http://localhost:8000/images/{output_filename}"
        }

    except Exception as e:
        return {
            "error": str(e)
        }