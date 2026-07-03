import streamlit as st
import requests

st.subheader("فحص الـ API")
if st.button("اختبار الاتصال بالسيرفر"):
    try:
        response = requests.get(f"{BASE_URL}/records")
        st.write(f"الحالة: {response.status_code}")
        st.write(f"المحتوى: {response.json()}")
    except Exception as e:
        st.error(f"تعذر الاتصال: {e}")
# إعدادات عنوان السيرفر
BASE_URL = "https://ashur-hospital-backend.onrender.com"

st.set_page_config(page_title="نظام المستشفى الآمن (RBAC)", layout="centered")

# CSS
st.markdown("""
<style>
@keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.7; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.7; }
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}
.medical-logo{
    font-size:70px;
    text-align:center;
    animation:float 3s ease-in-out infinite;
}
.pulse-heart{
    display:inline-block;
    animation:pulse 1.5s infinite;
    color:red;
}
</style>

<div class="medical-logo">
🏥<span class="pulse-heart">❤️‍🩹</span>🩺
</div>
""", unsafe_allow_html=True)

st.title("🏥 نظام إدارة المستشفى الإلكتروني الآمن")
st.subheader("نظام التحكم بالوصول القائم على الأدوار (RBAC)")

# Session
if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

st.sidebar.header("🔐 بوابة النظام")

if not st.session_state.token:

    menu = st.sidebar.selectbox(
        "اختر العملية",
        ["تسجيل دخول", "إنشاء حساب جديد"]
    )

    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")

    # إنشاء حساب
    if menu == "إنشاء حساب جديد":

        role = st.sidebar.selectbox(
            "اختر الدور الطبي",
            ["Admin", "Doctor", "Nurse", "Receptionist", "Patient"]
        )

        if st.sidebar.button("إنشاء الحساب"):

            res = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": username,
                    "password": password,
                    "role": role
                }
            )

            if res.status_code == 200:
                st.sidebar.success(
                    f"تم إنشاء الحساب بنجاح كـ {role}"
                )

            else:
                try:
                    st.sidebar.error(
                        res.json().get("detail", "حدث خطأ")
                    )
                except Exception:
                    st.sidebar.error(res.text)

    # تسجيل الدخول
    elif menu == "تسجيل دخول":

        if st.sidebar.button("دخول"):

            res = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            if res.status_code == 200:

                data = res.json()

                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.username = username

                st.rerun()

            else:
                try:
                    st.sidebar.error(
                        res.json().get("detail", "بيانات الدخول غير صحيحة")
                    )
                except Exception:
                    st.sidebar.error(res.text)

else:

    st.sidebar.success(f"مرحباً {st.session_state.username}")
    st.sidebar.info(f"الدور: {st.session_state.role}")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

# الواجهة الرئيسية
if not st.session_state.token:

    st.warning("يرجى تسجيل الدخول.")

else:

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    # الطبيب أو المدير
    if st.session_state.role in ["Doctor", "Admin"]:

        st.header("➕ إضافة سجل طبي")

        with st.form("record"):

            patient = st.text_input("اسم المريض")
            diagnosis = st.text_input("التشخيص")
            prescription = st.text_area("الوصفة")

            submit = st.form_submit_button("حفظ")

            if submit:

                payload = {
                    "patient_name": patient,
                    "diagnosis": diagnosis,
                    "prescription": prescription
                }

                res = requests.post(
                    f"{BASE_URL}/records",
                    json=payload,
                    headers=headers
                )

                if res.status_code == 200:
                    st.success("تم الحفظ بنجاح")
                else:
                    try:
                        st.error(res.json().get("detail"))
                    except Exception:
                        st.error(res.text)

    # عرض السجلات
    if st.session_state.role in ["Doctor", "Nurse", "Admin"]:

        st.header("📋 السجلات الطبية")

        if st.button("عرض السجلات"):

            res = requests.get(
                f"{BASE_URL}/records",
                headers=headers
            )

            if res.status_code == 200:

                records = res.json().get("records", [])

                if len(records) == 0:
                    st.info("لا توجد سجلات")
                    
                for rec in records:

                    with st.expander(rec["patient_name"]):
                        st.write("**التشخيص:**", rec["diagnosis"])
                        st.write("**الوصفة:**", rec["prescription"])

            else:
                try:
                    st.error(res.json().get("detail"))
                except Exception:
                    st.error(res.text)
