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

Tạo file `.env` từ `.env.example` và thiết lập các biến môi trường cần thiết:

```bash
copy .env.example .env
```

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

## Thực Tập Cloud Engineer - Báo Cáo Hạ Tầng (Infrastructure & Ops)

Dự án này đã được cấu hình và triển khai lên Google Cloud Platform (GCP) theo chuẩn tài liệu `Cloud_Engineer_Internship_Plan.pdf`. Dưới đây là các tài liệu liên quan đến kiến trúc và quy trình triển khai:

### 1. Kiến Trúc Hạ Tầng (Architecture)
- **Ứng dụng**: Stateless API được đóng gói bằng Docker (Multi-stage build).
- **Môi trường chạy**: Google Cloud Run, hỗ trợ auto-scaling (1 đến 5 instances cho production).
- **Lưu trữ**: Ảnh Docker được lưu trữ và versioning tại Google Artifact Registry.
- **Tích hợp**: MongoDB Atlas (Database) và AWS S3 (Storage).

### 2. Quy Trình CI/CD (Pipeline Flow)
- **Continuous Integration (CI)**: GitHub Actions (`ci.yml`) tự động kích hoạt khi có Push/PR vào nhánh `main`. Pipeline thực hiện build thử nghiệm Docker image, cấu hình caching để tăng tốc độ build.
- **Continuous Deployment (CD)**: GitHub Actions (`cd.yml`) xác thực an toàn lên GCP bằng **Workload Identity Federation** (OIDC), tự động build, push image lên Artifact Registry và deploy lên Cloud Run.

### 3. Hạ Tầng Bằng Code (IaC với sst.dev)
- Toàn bộ hạ tầng Cloud Run được định nghĩa bằng mã nguồn TypeScript (`sst.config.ts`).
- Tự động cấu hình biến môi trường, tài nguyên CPU/RAM theo từng môi trường (`stage`), và thiết lập quyền truy cập công khai (IAM Policy) mà không cần thao tác thủ công trên console.

### 4. IAM & Bảo Mật (Security & Access Control)
- **Container Security**: Ứng dụng bên trong Docker được thực thi bằng `non-root user` (`appuser`) nhằm tuân thủ nguyên tắc bảo mật.
- **Least-Privilege IAM**: Cấp quyền CI/CD cho GitHub Actions thông qua một Service Account chuyên biệt (`cardly-deployer-sa`) kết hợp với Workload Identity Pool.

### 5. Khắc Phục Sự Cố (Postmortem)
- **Vấn đề 1 (Build chậm & Image nặng)**: Việc cài đặt các thư viện Python cần biên dịch C++ làm chậm quá trình CI và làm phình to kích thước Docker image.
  - *Giải pháp*: Áp dụng Multi-stage build (tạo `wheels` ở builder stage rồi copy sang runner stage) và sử dụng Docker layer caching trong GitHub Actions.
- **Vấn đề 2 (Bảo mật thông tin xác thực)**: Sử dụng Service Account Key tĩnh dạng JSON trên GitHub Secrets tiềm ẩn rủi ro lộ lọt key dài hạn.
  - *Giải pháp*: Tích hợp Workload Identity Federation (WIF) để trao đổi trust token ngắn hạn giữa GitHub và GCP.
