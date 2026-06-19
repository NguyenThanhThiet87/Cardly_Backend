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
# Chỉ copy các gói wheels đã build xong từ Stage 1 sang
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
# Cài đặt từ wheels (nhanh và nhẹ hơn tải từ mạng rất nhiều)
RUN pip install --no-cache /wheels/*
# Copy mã nguồn
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
