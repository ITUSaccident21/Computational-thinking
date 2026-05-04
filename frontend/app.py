import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "")  # your-app.firebaseapp.com

FIREBASE_LOGIN_URL = (
    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={FIREBASE_API_KEY}"
)
FIREBASE_REGISTER_URL = (
    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    f"?key={FIREBASE_API_KEY}"
)

# ─── SESSION STATE INIT ────────────────────────────────────────────────────────
if "id_token" not in st.session_state:
    st.session_state.id_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ─── Đọc token từ Google login (qua query params) ─────────────────────────────
params = st.query_params
if "token" in params and "email" in params and not st.session_state.id_token:
    st.session_state.id_token = params["token"]
    st.session_state.user_email = params["email"]
    st.query_params.clear()
    st.rerun()

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def auth_header():
    return {"Authorization": f"Bearer {st.session_state.id_token}"}

def firebase_login(email: str, password: str) -> bool:
    resp = requests.post(FIREBASE_LOGIN_URL, json={
        "email": email, "password": password, "returnSecureToken": True,
    })
    if resp.status_code == 200:
        data = resp.json()
        st.session_state.id_token = data["idToken"]
        st.session_state.user_email = data["email"]
        return True
    st.error(f"Đăng nhập thất bại: {resp.json().get('error', {}).get('message', '')}")
    return False

def firebase_register(email: str, password: str) -> bool:
    resp = requests.post(FIREBASE_REGISTER_URL, json={
        "email": email, "password": password, "returnSecureToken": True,
    })
    if resp.status_code == 200:
        data = resp.json()
        st.session_state.id_token = data["idToken"]
        st.session_state.user_email = data["email"]
        return True
    st.error(f"Đăng ký thất bại: {resp.json().get('error', {}).get('message', '')}")
    return False

def logout():
    st.session_state.id_token = None
    st.session_state.user_email = None

def get_tasks():
    resp = requests.get(f"{BACKEND_URL}/tasks", headers=auth_header())
    return resp.json() if resp.status_code == 200 else []

def add_task(title: str):
    resp = requests.post(f"{BACKEND_URL}/tasks", json={"title": title}, headers=auth_header())
    return resp.status_code == 200

def toggle_task(task_id: str, current_done: bool):
    requests.patch(f"{BACKEND_URL}/tasks/{task_id}", json={"done": not current_done}, headers=auth_header())

def delete_task(task_id: str):
    requests.delete(f"{BACKEND_URL}/tasks/{task_id}", headers=auth_header())

# ─── Google Login Component ────────────────────────────────────────────────────
def google_login_button():
    html_code = f"""
    <script type="module">
        import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
        import {{ getAuth, GoogleAuthProvider, signInWithPopup }}
            from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

        const app = initializeApp({{ apiKey: "{FIREBASE_API_KEY}", authDomain: "{FIREBASE_AUTH_DOMAIN}" }});
        const auth = getAuth(app);
        const provider = new GoogleAuthProvider();

        document.getElementById("google-btn").addEventListener("click", async () => {{
            try {{
                const result = await signInWithPopup(auth, provider);
                const token = await result.user.getIdToken();
                const email = result.user.email;
                window.parent.location.href =
                    window.parent.location.pathname +
                    "?token=" + encodeURIComponent(token) +
                    "&email=" + encodeURIComponent(email);
            }} catch (err) {{
                document.getElementById("error-msg").innerText = "Lỗi: " + err.message;
            }}
        }});
    </script>
    <style>
        #google-btn {{
            display: flex; align-items: center; gap: 10px;
            background: white; border: 1px solid #dadce0; border-radius: 6px;
            padding: 10px 16px; font-size: 14px; font-family: sans-serif;
            cursor: pointer; color: #3c4043; width: 100%; justify-content: center;
        }}
        #google-btn:hover {{ background: #f8f9fa; }}
        #error-msg {{ color: red; font-size: 13px; margin-top: 8px; }}
    </style>
    <button id="google-btn">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="20"/>
        Đăng nhập với Google
    </button>
    <div id="error-msg"></div>
    """
    components.html(html_code, height=80)

# ─── UI ────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="📝 Todo App", page_icon="✅", layout="centered")
st.title("📝 Todo App")

if not st.session_state.id_token:
    tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab_login:
        st.subheader("Đăng nhập")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Mật khẩu", type="password", key="login_pass")
        if st.button("Đăng nhập", use_container_width=True):
            if email and password:
                if firebase_login(email, password):
                    st.rerun()
            else:
                st.warning("Vui lòng nhập đầy đủ email và mật khẩu.")
        st.divider()
        st.caption("Hoặc đăng nhập bằng:")
        google_login_button()

    with tab_register:
        st.subheader("Đăng ký tài khoản mới")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Mật khẩu (tối thiểu 6 ký tự)", type="password", key="reg_pass")
        if st.button("Đăng ký", use_container_width=True):
            if reg_email and reg_pass:
                if firebase_register(reg_email, reg_pass):
                    st.success("Đăng ký thành công!")
                    st.rerun()
            else:
                st.warning("Vui lòng nhập đầy đủ thông tin.")

else:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"👋 Xin chào, **{st.session_state.user_email}**")
    with col2:
        if st.button("Đăng xuất", use_container_width=True):
            logout()
            st.rerun()

    st.divider()
    st.subheader("➕ Thêm task mới")
    new_task = st.text_input("Nhập nội dung task", placeholder="Ví dụ: Học FastAPI")
    if st.button("Thêm", use_container_width=True):
        if new_task.strip():
            if add_task(new_task.strip()):
                st.success("Đã thêm task!")
                st.rerun()
        else:
            st.warning("Nội dung task không được để trống.")

    st.divider()
    st.subheader("📋 Danh sách task")
    tasks = get_tasks()

    if not tasks:
        st.info("Chưa có task nào. Hãy thêm task đầu tiên!")
    else:
        done_count = sum(1 for t in tasks if t["done"])
        st.caption(f"Hoàn thành: {done_count}/{len(tasks)}")
        for task in tasks:
            col_check, col_title, col_del = st.columns([1, 6, 1])
            with col_check:
                checked = st.checkbox("", value=task["done"], key=f"check_{task['id']}")
                if checked != task["done"]:
                    toggle_task(task["id"], task["done"])
                    st.rerun()
            with col_title:
                st.markdown(f"~~{task['title']}~~" if task["done"] else task["title"])
            with col_del:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    delete_task(task["id"])
                    st.rerun()