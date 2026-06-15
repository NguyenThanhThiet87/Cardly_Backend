# See https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PaddleOCR-VL.html to install/use
from paddleocr import PaddleOCRVL

# Khởi tạo pipeline PaddleOCR-VL phiên bản v1.5
pipeline = PaddleOCRVL(pipeline_version="v1.5")

# Chạy mô hình dự đoán trên ảnh bằng lái mẫu
image_path = "src/features/scans/sample/Australia-front-2-1024x609.jpg"
print(f"Đang chạy PaddleOCR-VL trên ảnh: {image_path}...")
output = pipeline.predict(image_path)

# In kết quả và lưu ra các định dạng cấu trúc
for res in output:
    res.print()
    res.save_to_json(save_path="output")
    res.save_to_markdown(save_path="output")
    print("\nĐã lưu thành công kết quả cấu trúc vào thư mục 'output/'!")
