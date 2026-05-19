# Cardly Backend

Backend API cho Cardly, xây bằng FastAPI và MongoDB. Project có các chức năng chính như auth, forgot password qua Gmail, quản lý user, contacts, digital cards, scans, events, tags và enrichment.

## Yêu Cầu

- Python 3.11+
- MongoDB Atlas hoặc MongoDB local
- Gmail có bật 2-Step Verification để tạo App Password
- Gemini API key nếu dùng chức năng scan/enrichment
- AWS S3 credentials nếu dùng upload/storage

## Cài Đặt

Tạo virtual environment:

```bash
python -m venv .venv
```

Kích hoạt virtual environment trên Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

Cài thư viện:

```bash
pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example`:

```bash
copy .env.example .env
```

Sau đó sửa các giá trị trong `.env` cho đúng tài khoản của bạn.

## Cấu Hình `.env`

Các biến quan trọng:

```env
MONGO_URI="mongodb+srv://<username>:<password>@<cluster-url>/?appName=Cluster0"
DB_NAME="Cardly"

SECRET_KEY="change-this-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:5173
RESET_PASSWORD_URL=http://localhost:8000/api/auth/reset-password

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_google_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_USE_TLS=true

GEMINI_API_KEY=your_gemini_api_key

AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_S3_REGION=ap-southeast-1
```

`SMTP_PASSWORD` phải là Google App Password, không phải mật khẩu Gmail bình thường.

## Chạy Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API docs:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

## Forgot Password

Flow quên mật khẩu:

1. User nhập email ở frontend.
2. Frontend gọi `POST /api/auth/forgot-password`.
3. Backend tạo reset token, lưu token dạng hash trong MongoDB.
4. Backend gửi link reset password qua Gmail.
5. User click link trong Gmail.
6. Trang reset password mở ra, user nhập mật khẩu mới.
7. Backend kiểm tra token và đổi mật khẩu.

Gọi API gửi email:

```http
POST /api/auth/forgot-password
Content-Type: application/json
```

Body:

```json
{
  "email": "user@gmail.com"
}
```

Response:

```json
{
  "message": "If the email exists, a password reset token has been generated"
}
```

Email sẽ chứa link dạng:

```text
http://localhost:8000/api/auth/reset-password?token=<reset_token>
```

Route đổi mật khẩu bằng API:

```http
POST /api/auth/reset-password
Content-Type: application/json
```

Body:

```json
{
  "token": "<reset_token>",
  "new_password": "Password1!"
}
```

Mật khẩu phải dài 8-16 ký tự và có ít nhất một chữ, một chữ hoa, một số, một ký tự đặc biệt.

## Auth Endpoints

Base URL:

```text
http://localhost:8000/api
```

Các endpoint chính:

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/forgot-password
GET  /auth/reset-password?token=<reset_token>
POST /auth/reset-password
GET  /auth/me
POST /auth/logout
```

Các route cần đăng nhập dùng header:

```http
Authorization: Bearer <access_token>
```

## Feature Routes

Một số route chính:

```text
/api/users/me
/api/contacts
/api/digital-cards
/api/public/{username}
/api/scans/upload
/api/events
/api/tags
/api/enrichment
```

Xem chi tiết request/response trong Swagger:

```text
http://localhost:8000/docs
```

## Lỗi Thường Gặp

Nếu forgot password báo thiếu SMTP config, kiểm tra các biến:

```env
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_USE_TLS
```

Nếu Gmail không gửi được, kiểm tra:

- Gmail đã bật 2-Step Verification.
- `SMTP_PASSWORD` là App Password.
- Không có khoảng trắng thừa ở đầu dòng `.env`, ví dụ dùng `FRONTEND_URL=http://localhost:5173`.

Nếu click link reset password bị về trang login frontend, dùng:

```env
RESET_PASSWORD_URL=http://localhost:8000/api/auth/reset-password
```

Sau khi sửa `.env`, restart backend.

## Test Nhanh

Compile module auth:

```bash
python -m compileall src/features/auth
```

Chạy test nếu đã cài pytest:

```bash
pytest
```
