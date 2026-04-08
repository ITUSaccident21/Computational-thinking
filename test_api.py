import requests

url = "http://127.0.0.1:8000/predict"
file_path = "Test.jpeg" # Tấm ảnh bạn để trong thư mục

with open(file_path, "rb") as f:
    response = requests.post(url, files={"file": f})
    print(response.json())