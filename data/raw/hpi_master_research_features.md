# Tài liệu Đặc tả Dữ liệu: Dự đoán Chỉ số Giá nhà (HPI)

## 1. Tổng quan Dự án
Bộ dữ liệu này được tổng hợp và xử lý từ các nguồn dữ liệu thô của **Cơ quan Tài chính Nhà ở Liên bang (FHFA)** theo định kỳ hàng quý. Đây là kết quả của quá trình tích hợp nhiều tệp tin (`.xlsx`) để tạo ra một cơ sở dữ liệu thống nhất phục vụ nghiên cứu khoa học về dự báo bất động sản.

- **Đơn vị thời gian:** Hàng quý (Quarterly).
- **Phạm vi:** 1992 - 2025.
- **Đối tượng:** 100 khu vực đô thị (CBSA) trọng điểm tại Hoa Kỳ.
- **Phương pháp:** Kết hợp dữ liệu đa tầng (Multi-level Join) và Kỹ thuật tạo đặc trưng (Feature Engineering).

---

## 2. Quy trình Xử lý Dữ liệu (ETL)
Dữ liệu được hình thành từ việc kết hợp (Join) các nguồn sau:
1. **Cấp độ Metro:** Lấy từ tệp chỉ số khu vực đô thị làm bảng gốc.
2. **Cấp độ Bang (State):** Trích xuất mã bang từ tên khu vực và kết nối với chỉ số giá nhà cấp bang.
3. **Cấp độ Quốc gia (USA):** Kết nối chỉ số toàn nước Mỹ dựa trên thời gian (Năm/Quý).
4. **Chỉ số Distress-Free:** Tích hợp dữ liệu giao dịch sạch để đối chiếu biến động nợ xấu.

---

## 3. Danh mục các cột dữ liệu (Data Dictionary)

### A. Nhóm thông tin cơ bản
| Tên cột | Ý nghĩa |
| :--- | :--- |
| `cbsa` | Mã định danh khu vực đô thị. |
| `metro_name` | Tên khu vực đô thị (Ví dụ: "Worcester, MA"). |
| `year` | Năm ghi nhận dữ liệu. |
| `quarter` | Quý ghi nhận (1, 2, 3, 4). |
| `state` | Mã bưu điện của bang (Ví dụ: NY, MA, CA). |
| `time_trend` | Chỉ số thời gian lũy tiến (1, 2, 3...). |

### B. Nhóm Chỉ số Giá nhà (Core HPI)
| Tên cột | Ý nghĩa |
| :--- | :--- |
| `hpi_metro_sa` | **Biến mục tiêu (Target)**: Chỉ số giá nhà khu vực (đã điều chỉnh mùa vụ). |
| `hpi_metro_nsa` | Chỉ số giá nhà khu vực (chưa điều chỉnh mùa vụ). |
| `hpi_metro_df_sa` | Chỉ số giá nhà loại bỏ các giao dịch phát mãi (Distress-Free). |
| `hpi_state_sa` | Chỉ số giá nhà trung bình của toàn bang. |
| `hpi_usa_sa` | Chỉ số giá nhà trung bình toàn quốc (Dùng làm mốc tham chiếu). |

### C. Nhóm Đặc trưng Kỹ thuật (Engineered Features)
*Đây là nhóm cột quan trọng nhất để tăng độ chính xác cho mô hình Machine Learning.*

- **Biến trễ (Lags):** `hpi_lag_1` đến `hpi_lag_8` (Giá của các quý trước đó).
- **Tăng trưởng:** `qoq_growth` (tăng trưởng theo quý) và `yoy_growth` (tăng trưởng theo năm).
- **Động lực:** `growth_velocity` (sự thay đổi của tốc độ tăng trưởng).
- **Rủi ro:** `volatility_4q` (độ biến động giá trong 1 năm gần nhất).
- **So sánh:** `metro_to_state_ratio` và `metro_to_usa_ratio` (vị thế giá khu vực so với bang/quốc gia).
- **Chu kỳ:** `q_sin` và `q_cos` (mô hình hóa tính tuần hoàn của các mùa trong năm).
- **Đỉnh giá:** `pct_from_peak` (đo lường mức độ sụt giảm so với đỉnh lịch sử).

---

## 4. Hướng dẫn cho Nhà nghiên cứu
- **Tiền xử lý:** Các dòng đầu tiên của mỗi khu vực sẽ có giá trị `NaN` ở các cột trễ. Khuyến nghị xóa các dòng này trước khi đưa vào huấn luyện.
- **Tương quan:** Các cột `hpi_lag_n` thường có tương quan rất cao với `hpi_metro_sa`. Cân nhắc sử dụng mô hình dạng Gradient Boosting (XGBoost) để xử lý tốt nhất.
- **Chia dữ liệu:** Nên chia tập Train/Test theo mốc thời gian (ví dụ: Train < 2021, Test >= 2021) để tránh hiện tượng rò rỉ dữ liệu (data leakage).

---
*Nguồn dữ liệu: Federal Housing Finance Agency (FHFA).*
