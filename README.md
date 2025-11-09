# FFmpeg Video Trimmer

Ứng dụng GUI đơn giản giúp cắt video nhanh chóng bằng FFmpeg.

## Yêu cầu

- Python 3.7+
- [FFmpeg](https://ffmpeg.org/) (ffmpeg.exe và ffprobe.exe đặt cùng thư mục với `main.py` hoặc đã thêm vào PATH)
- Thư viện Tkinter (thường có sẵn với Python)

## Cài đặt

1. Cài đặt Python nếu chưa có.
2. Đảm bảo FFmpeg đã được cài đặt và có thể truy cập từ dòng lệnh.
3. Cài đặt các thư viện cần thiết:
    ```sh
    pip install -r requirements.txt
    ```

## Sử dụng

1. Chạy chương trình:
    ```sh
    python main.py
    ```
2. Chọn file video đầu vào và thư mục lưu file đầu ra.
3. Nhập timecode bắt đầu và kết thúc (định dạng `hh:mm:ss`).
4. Nhấn nút **Cắt** để thực hiện cắt video.

## Ghi chú

- Nếu không tìm thấy FFmpeg, hãy tải về từ [ffmpeg.org](https://ffmpeg.org/download.html) và đặt file `ffmpeg.exe` cùng thư mục với `main.py`.
- Ứng dụng hỗ trợ các định dạng video phổ biến như `.mp4`, `.mov`, `.avi`, `.mkv`, `.mxf`.

## License

MIT
