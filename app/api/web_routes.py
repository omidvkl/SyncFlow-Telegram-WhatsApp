import secrets
import random
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os

from app.db.database import get_db
from app.db import crud
from app.db import models
from app.core.config import settings
from app.core import security

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# --- وابستگی‌ها (Dependencies) برای امنیت سیستم ---
async def get_current_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username != settings.ADMIN_USERNAME:
            return None
        return username
    except JWTError:
        return None

async def require_admin(request: Request):
    admin = await get_current_admin(request)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return admin

# --- مسیرهای پنل کاربری ---

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request, admin=Depends(get_current_admin)):
    if admin:
        return RedirectResponse(url="/", status_code=302)
        
    # تولید کپچای ریاضی
    num1, num2 = random.randint(1, 10), random.randint(1, 10)
    operators = {'+': lambda a, b: a + b, '-': lambda a, b: a - b, '×': lambda a, b: a * b}
    op_char = random.choice(list(operators.keys()))
    
    correct_answer = operators[op_char](num1, num2)
    request.session['captcha_ans'] = correct_answer
    
    captcha_text = f"{num1} {op_char} {num2}"
    
    return templates.TemplateResponse("login.html", {"request": request, "captcha_text": captcha_text})

@router.post("/login")
async def login_post(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    captcha_answer: int = Form(...)
):
    # بررسی کپچای ریاضی
    if request.session.get('captcha_ans') != captcha_answer:
        return RedirectResponse(url="/login?error=captcha", status_code=302)

    # مقایسه ایمن بایت به بایت برای جلوگیری از هک (Timing Attacks)
    is_correct_username = secrets.compare_digest(
        username.encode("utf8"), 
        settings.ADMIN_USERNAME.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        password.encode("utf8"), 
        settings.ADMIN_PASSWORD.encode("utf8")
    )

    if is_correct_username and is_correct_password:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        res = RedirectResponse(url="/", status_code=302)
        res.set_cookie(
            key="access_token", 
            value=f"Bearer {access_token}", 
            httponly=True, 
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        return res
    
    return RedirectResponse(url="/login?error=invalid_credentials", status_code=302)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        await require_admin(request)
    except HTTPException as e:
        return RedirectResponse(url=e.headers["Location"], status_code=e.status_code)
        
    sys_settings = crud.get_settings(db)
    logs = crud.get_logs(db, limit=100) 
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "settings": sys_settings, "logs": logs}
    )

@router.post("/settings")
async def save_settings(
    request: Request,
    whapi_token: str = Form(None),
    whatsapp_channel_id: str = Form(None),
    telegram_channel_id: str = Form(None),
    is_sync_active: bool = Form(False),
    link1_title: str = Form(""), link1_url: str = Form(""),
    link2_title: str = Form(""), link2_url: str = Form(""),
    link3_title: str = Form(""), link3_url: str = Form(""),
    link4_title: str = Form(""), link4_url: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        await require_admin(request)
    except HTTPException as e:
        return RedirectResponse(url=e.headers["Location"], status_code=e.status_code)
        
    update_data = {
        "whapi_token": whapi_token,
        "whatsapp_channel_id": whatsapp_channel_id,
        "telegram_channel_id": telegram_channel_id,
        "is_sync_active": is_sync_active,
        "link1_title": link1_title, "link1_url": link1_url,
        "link2_title": link2_title, "link2_url": link2_url,
        "link3_title": link3_title, "link3_url": link3_url,
        "link4_title": link4_title, "link4_url": link4_url,
    }
    crud.update_settings(db, update_data)
    return RedirectResponse(url="/?success=saved", status_code=302)

@router.get("/api/stats")
async def get_publish_stats(request: Request, filter_type: str = Query("all_time"), db: Session = Depends(get_db)):
    try:
        await require_admin(request)
    except:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    now = datetime.utcnow()
    query = db.query(models.SyncLog).filter(models.SyncLog.status == "success")
    
    if filter_type == "yesterday":
        start_date = now - timedelta(days=1)
        query = query.filter(models.SyncLog.created_at >= start_date)
    elif filter_type == "last_month":
        start_date = now - timedelta(days=30)
        query = query.filter(models.SyncLog.created_at >= start_date)
        
    count = query.count()
    return {"count": count}