# Todo App

Ứng dụng to-do gồm:
- Backend: FastAPI
- Frontend: Streamlit
- Xác thực: Firebase Email/Password và Google login
- Lưu trữ: Firestore

## Cài đặt

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Cấu hình

Tạo file `frontend/.env`:

```env
FIREBASE_API_KEY=your_web_api_key_here
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
BACKEND_URL=http://localhost:8000
```

Nếu dùng Firebase thật, đặt thêm `serviceAccountKey.json` vào `backend/` hoặc cấu hình biến `FIREBASE_CREDENTIALS` trỏ tới file đó.

## Chạy project

Terminal 1:

```bash
cd backend
uvicorn main:app --reload
```

Terminal 2:

```bash
cd frontend
streamlit run app.py
```

## Ghi chú

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:8501`
- File `.venv/`, `.env`, và `serviceAccountKey.json` không nên commit lên GitHub.