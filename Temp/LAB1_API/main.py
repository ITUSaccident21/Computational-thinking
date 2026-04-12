from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
from PIL import Image
import io
app = FastAPI()


detector = pipeline("object-detection", model="yainage90/fashion-object-detection")

@app.get("/")
def root():
    return {"message": "API Nhận diện trang phục của Trí"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
   
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    

    results = detector(image)
    
  
    return {"objects_detected": results}