import requests

# 1. Cấu hình các thông số
URL = "http://127.0.0.1:8000/predict"
IMAGE_PATH = "Test2.jpeg"  # Đảm bảo file này nằm cùng thư mục với code

def test_fashion_api():
    print(f"--- Đang gửi ảnh '{IMAGE_PATH}' tới API ---")
    
    try:
        # 2. Mở file ảnh ở chế độ binary (rb)
        with open(IMAGE_PATH, "rb") as f:
            # Gửi request POST kèm file
            # 'file' là tên tham số mà bạn đặt trong main.py (UploadFile)
            files = {"file": (IMAGE_PATH, f, "image/jpeg")}
            response = requests.post(URL, files=files)

        # 3. Kiểm tra mã trạng thái (Status Code)
        if response.status_code == 200:
            print("✅ Kết nối thành công!")
            data = response.json()
            
            # 4. Hiển thị kết quả đẹp mắt
            print("\n[KẾT QUẢ NHẬN DIỆN]")
            objects = data.get("objects_detected", [])
            
            if not objects:
                print("Không tìm thấy đồ thời trang nào trong ảnh.")
            else:
                for i, obj in enumerate(objects, 1):
                    label = obj.get("label")
                    score = obj.get("score")
                    print(f"{i}. Vật thể: {label} | Độ tự tin: {score:.2%}")
        else:
            print(f"❌ Lỗi hệ thống: {response.status_code}")
            print(response.text)

    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file ảnh '{IMAGE_PATH}'. Hãy kiểm tra lại tên file!")
    except requests.exceptions.ConnectionError:
        print("❌ Lỗi: Không thể kết nối tới Server. Bạn đã chạy lệnh 'uvicorn' chưa?")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    test_fashion_api()