# Cloud Run Infrastructure Architecture

Tài liệu này mô tả kiến trúc hạ tầng của dự án Cardly Backend, được quản lý 100% bằng mã nguồn (Infrastructure as Code) thông qua SST v3 (Ion) và Pulumi GCP.

## 1. Tổng quan Kiến trúc (Overview)
- **Framework quản lý IaC:** SST v3 (Ion) kết hợp với `@pulumi/gcp`.
- **State Backend:** Lưu trữ trạng thái cấu hình trên AWS SSM/S3 (quản lý tự động bởi SST).
- **Dịch vụ Core:** Google Cloud Run (v2).
- **Region:** `asia-southeast1` (Singapore) để tối ưu độ trễ (latency) về Việt Nam.

## 2. Chi tiết Cấu hình Cloud Run (Service Configuration)
Dịch vụ Backend API được chứa trong Docker Container và chạy Serverless trên nền tảng Cloud Run.

### 2.1. Cấu trúc Môi trường (Environments)
Hạ tầng thay đổi linh hoạt dựa trên biến `$app.stage` của SST:
- **Stage `prod`:**
  - Resource Limits: RAM 1024Mi, 1 CPU.
  - Scaling: Auto-scale lên tối đa 5 instances.
  - Protection: Bật tính năng `protect` và `retain` để tránh việc vô tình xóa database/tài nguyên trên production.
- **Stage `dev`/`staging`:**
  - Resource Limits: RAM 512Mi, 1 CPU (Tiết kiệm chi phí).
  - Scaling: Tối đa 1 instance.
  - Protection: Chế độ `remove`, tự động dọn dẹp sạch sẽ tài nguyên khi chạy lệnh `sst remove`.

### 2.2. Networking & Bảo mật (IAM)
- **Ingress:** Dịch vụ mở cổng (container port) `8000` theo cấu hình của Dockerfile.
- **IAM Policy:** Gắn quyền `roles/run.invoker` cho `allUsers`. Điều này cho phép API truy cập công khai từ Internet (Public Access), phù hợp với một Backend REST API thông thường.

## 3. Quy trình Deploy (Deployment Flow)
1. Lập trình viên đẩy Docker Image lên Google Artifact Registry.
2. Cập nhật đường link Image vào file `sst.config.ts`.
3. Chạy lệnh `npx sst deploy --stage <tên-stage>`.
4. SST so sánh (diff) hạ tầng, gọi API của GCP để tự động cấp phát tài nguyên.
5. URL của dịch vụ được xuất (Output) trực tiếp ra màn hình Terminal.
