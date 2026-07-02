from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI(title="Secure Hospital System Backend")

# قواعد بيانات مؤقتة في الذاكرة (للتجربة)
users_db: Dict[str, dict] = {}
records_db: List[dict] = []

# نماذج البيانات (Pydantic Models)
class RegisterModel(BaseModel):
    username: str
    password: str
    role: str

class LoginModel(BaseModel):
    username: str
    password: str

class RecordModel(BaseModel):
    patient_name: str
    diagnosis: str
    prescription: str

# مسار إنشاء حساب جديد
@app.post("/auth/register")
def register(user: RegisterModel):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="اسم المستخدم مسجل مسبقاً")
    
    # حفظ المستخدم ودوره الطبي
    users_db[user.username] = {
        "username": user.username,
        "password": user.password,  # في نظام حقيقي يتم تشفيرها
        "role": user.role
    }
    return {"message": "تم إنشاء الحساب بنجاح"}

# مسار تسجيل الدخول
@app.post("/auth/login")
def login(user: LoginModel):
    if user.username not in users_db or users_db[user.username]["password"] != user.password:
        raise HTTPException(status_code=400, detail="اسم المستخدم أو كلمة المرور غير صحيحة")
    
    # توليد توكن وهمي بسيط للتجربة والدور
    return {
        "access_token": f"mock-token-{user.username}",
        "role": users_db[user.username]["role"]
    }

# مسار إضافة السجلات الطبية
@app.post("/records")
def add_record(record: RecordModel):
    records_db.append(record.dict())
    return {"message": "تم حفظ السجل بنجاح"}

# مسار استعراض السجلات الطبية
@app.get("/records")
def get_records():
    return {"records": records_db}