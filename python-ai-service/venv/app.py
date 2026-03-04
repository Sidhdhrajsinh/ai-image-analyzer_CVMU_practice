from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
from fastapi import FastAPI, File, UploadFile
import shutil
import os
import time

app = FastAPI()

UPLOAD_FOLDER = "temp_uploads"

# Create folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)

        # Save uploaded file temporarily
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image.file.close()
        print(f"[AI SERVICE] Image received: {file_path}")

        # Simulate AI processing delay
        # time.sleep(2)

        # AI Processing
        img = cv2.imread(file_path)

        if img is None:
            raise Exception("Invalid image file")

        results = model(img)

        person_count = 0

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf > 0.5:  # person with confidence filter
                    person_count += 1

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # draw rectangle
                    cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)

                    # add label
                    label = f"Person {conf:.2f}"
                    cv2.putText(img, label, (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0,255,0),
                                2)
                    
        output_path = os.path.join(UPLOAD_FOLDER, f"annotated_{int(time.time())}_{image.filename}")
        cv2.imwrite(output_path, img)

        print(f"[AI SERVICE] Annotated image saved: {output_path}")
        
        print(f"[AI SERVICE] Persons detected: {person_count}")
        
        if person_count == 0:
            description = "No person detected in the image."
        elif person_count == 1:
            description = "1 person detected in the image."
        else:
            description = f"{person_count} persons detected in the image."
        
        # Delete file after processing
        os.remove(file_path)

        return {
            "description": description
        }

    except Exception as e:
        return {
            "error": str(e)
        }