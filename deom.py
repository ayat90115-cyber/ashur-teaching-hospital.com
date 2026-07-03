import streamlit as st
import requests

# 1. إعدادات عنوان السيرفر (FastAPI)
BASE_URL = "https://ashur-hospital-backend.onrender.com"

st.set_page_config(page_title="نظام المستشفى الآمن (RBAC)", layout="centered")

# --- إضافة أنيميشن طبي تفاعلي ومتحرك مدمج مباشرة عبر CSS ---
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
    .medical-logo {
        font-size: 70px;
        text-align: center;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 5px;
    }
    .pulse-heart {
        display: inline-block;
        animation: pulse 1.5s infinite;
        color: #ff4b4b;
    }
    </style>
    <div class="medical-logo">🏥<span class="pulse-heart">❤️‍🩹</span>🩺</div>
""", unsafe_allow_html=True)

st.title("🏥 نظام إدارة المستشفى الإلكتروني الآمن")
st.subheader("نظام التحكم بالوصول القائم على الأدوار (RBAC)")

# إدارة الجلسة (Session State) لحفظ التوكن ودور المستخدم
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- القائمة الجانبية (تسجيل الدخول / الخروج) ---
st.sidebar.header("🔐 بوابة تسجيل الدخول")

if not st.session_state.token:
    menu = st.sidebar.selectbox("اختر العملية", ["تسجيل دخول", "إنشاء حساب جديد"])
    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")
    
    if menu == "إنشاء حساب جديد":
        role = st.sidebar.selectbox("اختر الدور الطبي", ["Admin", "Doctor", "Nurse", "Receptionist", "Patient"])
        if st.sidebar.button("إنشاء الحساب"):
            res = requests.post(f"{BASE_URL}/auth/register", json={"username": username,
                                                                   "password": password,
                                                                   "role":role})
            if res.status_code == 200:
                st.sidebar.success(f"تم تسجيلك بنجاح كـ {role}! يمكنك الآن تسجيل الدخول.")
            else:
                try:
                st.sidebar.error(res.json().get("detail", "حدث خطأ ما"))
                except:
                st.sidebar.error(res.text)
    elif menu == "تسجيل دخول":
        if st.sidebar.button("دخول"):
            res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.username = username
                st.rerun()
            else:
                st.sidebar.error("اسم المستخدم أو كلمة المرور غير صحيحة")
else:
    st.sidebar.success(f"مرحباً: {st.session_state.username}")
    st.sidebar.info(f"الدور الحالي: {st.session_state.role}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

# --- واجهة النظام الرئيسية بناءً على الأدوار (RBAC) ---
if not st.session_state.token:
    st.warning("رجاءً قم بتسجيل الدخول من القائمة الجانبية للوصول إلى النظام.")
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    # 1. قسم إضافة السجلات (متاح فقط للأطباء والمدراء)
    if st.session_state.role in ["Doctor", "Admin"]:
        st.write("---")
        st.header("✍️ إضافة سجل طبي جديد (صلاحية الطبيب/المدير)")
        with st.form("add_record_form"):
            p_name = st.text_input("اسم المريض")
            p_diag = st.text_input("التشخيص الطبي")
            p_presc = st.text_area("الوصفة الطبية والعلاج")
            submit = st.form_submit_button("حفظ السجل في قاعدة البيانات")
            
            if submit:
                payload = {"patient_name": p_name, "diagnosis": p_diag, "prescription": p_presc}
                res = requests.post(f"{BASE_URL}/records", json=payload, headers=headers)
                if res.status_code == 200:
                    st.success("تم حفظ السجل الطبي بنجاح!")
                else:
                    st.error(res.json().get("detail"))

    # 2. قسم استعراض السجلات (متاح للأطباء، الممرضين، والمدراء)
    if st.session_state.role in ["Doctor", "Nurse", "Admin"]:
        st.write("---")
        st.header("📋 استعراض السجلات الطبية (صلاحية الطاقم الطبي)")
        if st.button("تحديث وعرض البيانات"):
            res = requests.get(f"{BASE_URL}/records", headers=headers)
            if res.status_code == 200:
                records = res.json().get("records", [])
                if not records:
                    st.info("لا توجد سجلات مرضى حالياً.")
                for rec in records:
                    with st.expander(f"🏥 المريض: {rec['patient_name']}"):
                        st.write(f"**التشخيص:** {rec['diagnosis']}")
                        st.write(f"**الوصفة الطبية:** {rec['prescription']}")
            else:
                st.error("فشل جلب البيانات: " + res.json().get("detail"))
