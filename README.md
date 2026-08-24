# Smart Gate Vehicle Monitor & Tracker

Ứng dụng desktop viết bằng Python (sử dụng PySide6, OpenCV và YOLOv8) giúp giám sát cổng ra vào, tự động nhận diện và đếm số lượng phương tiện đi qua cổng, đồng thời lưu trữ lịch sử dịch chuyển và hỗ trợ cắt xuất video sự kiện.

## Tính năng nổi bật

- **Xem trực tiếp video**: Hỗ trợ mở các tệp tin video phổ biến (MP4, AVI, MKV, MOV).
- **Vẽ đường ranh giới động (Draw Gate)**: Người dùng có thể nhấn nút "Draw Gate" rồi kéo thả trực tiếp trên màn hình video để điều chỉnh vị trí cổng cần đếm.
- **Đếm phương tiện theo hướng (In/Out)**:
  - Phân loại 4 nhóm chính: Ô tô, Xe máy, Xe tải, Xe buýt.
  - Phân biệt hướng di chuyển của phương tiện (đi vào hoặc đi ra) dựa trên ranh giới đã vẽ.
  - Vẽ đuôi quỹ đạo bám vết của phương tiện.
- **Nhật ký di chuyển thời gian thực (Activity Log)**: Ghi lại số thứ tự, thời điểm xảy ra (Timestamp), loại phương tiện, ID bám vết và hướng dịch chuyển. Hỗ trợ xuất nhật ký ra tệp tin CSV.
- **Cắt đoạn video tại local (Clipper)**:
  - **Cắt tự động theo sự kiện**: Nhấn nút "Save Clip" bên cạnh bất kỳ sự kiện nào để trích xuất nhanh đoạn video chứa sự kiện đó (từ 3 giây trước đến 3 giây sau sự kiện).
  - **Cắt thủ công**: Nhập thời điểm bắt đầu và thời lượng để xuất bất kỳ đoạn video nào tùy ý.
  - Quá trình cắt chạy trên luồng phụ độc lập (QThread), không gây đơ/đóng băng giao diện chính.

## Yêu cầu hệ thống

- Python 3.10 trở lên.
- Nên dùng GPU nếu muốn xử lý thời gian thực tốc độ cao (YOLO sẽ tự động kích hoạt CUDA nếu có). Trên CPU thông thường ứng dụng vẫn hoạt động mượt mà với phiên bản YOLOv8 Nano (`yolov8n.pt`).

## Hướng dẫn cài đặt

1. Mở thư mục dự án trong PyCharm hoặc Terminal.
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
   *Lưu ý: Quá trình cài đặt `ultralytics` sẽ tự động tải các gói phụ thuộc như PyTorch, NumPy và OpenCV.*

## Hướng dẫn chạy ứng dụng

Chạy tệp tin `main.py` từ Terminal hoặc nhấn nút Run trong PyCharm:
```bash
python main.py
```

## Cách sử dụng

1. **Tải video**: Nhấn nút **📂 Open Video** để chọn tệp tin video camera giám sát của bạn.
2. **Cài đặt cổng giám sát**:
   - Mặc định sẽ có một cổng nằm ngang ở giữa màn hình.
   - Để vẽ cổng mới, nhấn nút **✏ Draw Gate**, sau đó nhấp chuột trái và kéo vẽ một đoạn thẳng ngang qua làn đường trên khung hình video.
3. **Chạy/Tạm dừng**:
   - Nhấn **▶ Play** để bắt đầu đếm.
   - Nhấn **⏸ Pause** để tạm dừng.
   - Sử dụng thanh trượt (slider) dưới video để tua nhanh/chậm hoặc di chuyển tới khung hình mong muốn.
4. **Cắt đoạn video**:
   - Để lưu trữ lại khoảnh khắc xe đi qua cổng: trong cột **Action** của bảng nhật ký, nhấn nút **Save Clip** tương ứng. Đoạn video ngắn sẽ được xuất ra thư mục cục bộ `output/clips/`.
   - Để cắt thủ công, điền mốc thời gian và thời lượng ở mục **MANUAL VIDEO CLIPPER** rồi chọn **Export Custom Clip**.
5. **Xuất báo cáo**: Nhấn **Export Log to CSV** ở góc phải dưới bảng nhật ký để lưu lại file báo cáo Excel/CSV.
"# Vihecle-counting-" 
