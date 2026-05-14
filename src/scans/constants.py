import re

# Regex chuẩn để tìm kiếm trong văn bản (không dùng ^ và $)
REGEX_PHONE = r"(?:\+?\d{1,4}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4,}"
REGEX_EMAIL = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
REGEX_URL = r"(https?://|www\.)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/[^\s]*)?"

# Danh sách các từ khóa để nhận diện chức vụ (Position)
POSITION_KEYWORDS = [
    "CEO", "Founder", "Manager", "Director", "Engineer", "Developer", 
    "Consultant", "Specialist", "Partner", "Sales", "Executive", "GĐ", "Trưởng phòng",
    "Chủ tịch", "Giám đốc", "Sáng lập", "Kỹ sư"
]
