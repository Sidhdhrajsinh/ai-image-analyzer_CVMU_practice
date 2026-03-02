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

        print(f"Image received: {file_path}")

        # Simulate AI processing delay
        time.sleep(2)

        # Fake AI response
        description = "This is a mock AI-generated description of the uploaded image."

        # Delete file after processing
        os.remove(file_path)

        return {
            "description": description
        }

    except Exception as e:
        return {
            "error": str(e)
        }