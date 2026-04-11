from fastapi import FastAPI, UploadFile, File
from transformers import pipeline
from PIL import Image
import io
app = FastAPI()


detector = pipeline("object-detection", model="yainage90/fashion-object-detection")
# 1. Endpoint giới thiệu
@app.get("/")
def root():
    return {"message": "API Nhận diện thời trang của Trí"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1. Đọc file ảnh từ người dùng gửi lên
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))
    
    # 2. Đưa ảnh vào AI để nhận diện
    results = detector(image)
    
    # 3. Trả kết quả về dạng JSON
    return {"objects_detected": results}