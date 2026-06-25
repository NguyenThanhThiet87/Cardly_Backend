# --- Stage 1: Builder (Dùng để cài thư viện) ---
FROM python:3.11-slim as builder
WORKDIR /app
# Cài compiler nếu cần (để build các thư viện lõi C++)
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
# Cài thư viện vào một thư mục ảo (tạo wheels) thay vì cài thẳng
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --- Stage 2: Runner (Môi trường chạy thực tế siêu nhẹ) ---
FROM python:3.11-slim
WORKDIR /app

# 1. Cài đặt thư viện khi VẪN ĐANG LÀ ROOT (để pip có quyền ghi vào hệ thống)
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# 2. Copy mã nguồn (vẫn đang là root)
COPY . .

# 3. CHUẨN BẢO MẬT: Tạo user và CHUYỂN QUYỀN SỞ HỮU thư mục code cho user đó
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

# 4. Kích hoạt user ẩn danh (Phải nằm sát cuối)
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]