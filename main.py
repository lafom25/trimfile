import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import threading
from pathlib import Path
import re
import json

class FFmpegTrimmerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Video Trimmer")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.timecode_in = tk.StringVar(value="00:00:00")
        self.timecode_out = tk.StringVar(value="00:01:00")
        self.ffmpeg_path = self.get_ffmpeg_path()
        self.video_duration = None
        
        # Setup GUI
        self.setup_ui()
        
    def get_ffmpeg_path(self):
        """Tìm ffmpeg trong thư mục gốc của chương trình"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_exe = os.path.join(base_path, "ffmpeg.exe")
        ffmpeg_bin = os.path.join(base_path, "ffmpeg")
        
        if os.path.exists(ffmpeg_exe):
            return ffmpeg_exe
        elif os.path.exists(ffmpeg_bin):
            return ffmpeg_bin
        else:
            return "ffmpeg"
    
    def setup_ui(self):
        """Tạo giao diện người dùng"""
        # Frame chính
        main_frame = tk.Frame(self.root, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === INPUT FILE ===
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(input_frame, text="Input File:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Entry(input_frame, textvariable=self.input_file, width=45, state="readonly").pack(side=tk.LEFT, padx=10)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT)
        
        # === OUTPUT FOLDER ===
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(output_frame, text="Output Folder:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_folder, width=45, state="readonly").pack(side=tk.LEFT, padx=10)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT)
        
        # === TIME CODE ===
        timecode_frame = tk.Frame(main_frame)
        timecode_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(timecode_frame, text="Time Code In:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        tk.Entry(timecode_frame, textvariable=self.timecode_in, width=15).pack(side=tk.LEFT, padx=10)
        
        tk.Label(timecode_frame, text="Time Code Out:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        tk.Entry(timecode_frame, textvariable=self.timecode_out, width=15).pack(side=tk.LEFT, padx=10)
        
        # === BUTTONS ===
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="Cắt", command=self.trim_video, bg="#4CAF50", 
                 fg="white", font=("Arial", 11, "bold"), padx=20, pady=10).pack()
        
        # === STATUS TEXT BOX ===
        tk.Label(main_frame, text="Trạng thái:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(20, 5))
        
        self.status_text = tk.Text(main_frame, height=12, width=80, state="disabled", 
                                   bg="#f5f5f5", fg="#333", font=("Courier", 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(main_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
    
    def browse_input(self):
        """Chọn file input"""
        file_path = filedialog.askopenfilename(
            title="Chọn file để cắt",
            filetypes=[("Video files", "*.mxf *.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)
            self.video_duration = None
    
    def browse_output(self):
        """Chọn folder output"""
        folder_path = filedialog.askdirectory(title="Chọn folder lưu file output")
        if folder_path:
            self.output_folder.set(folder_path)
    
    def validate_timecode(self, timecode):
        """Kiểm tra định dạng timecode (hh:mm:ss)"""
        pattern = r'^(\d{1,2}):(\d{2}):(\d{2})$'
        if not re.match(pattern, timecode):
            return False
        return True
    
    def timecode_to_seconds(self, timecode):
        """Chuyển đổi timecode sang giây"""
        parts = timecode.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_timecode(self, seconds):
        """Chuyển đổi giây sang timecode"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_video_duration(self, file_path):
        """Lấy duration của file bằng ffprobe hoặc ffmpeg"""
        try:
            # Cố gắng dùng ffprobe
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg.exe", "ffprobe.exe").replace("ffmpeg", "ffprobe")
            
            command = [
                ffprobe_path,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:noesc=1",
                file_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    duration = float(result.stdout.strip())
                    return duration
                except ValueError:
                    pass
        except:
            pass
        
        # Nếu ffprobe không có, dùng ffmpeg để lấy duration
        try:
            command = [self.ffmpeg_path, "-i", file_path]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            
            # Tìm Duration trong output
            output = result.stderr
            match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', output)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = float(match.group(3))
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds
        except:
            pass
        
        return None
    
    def add_status(self, message):
        """Thêm message vào status text box"""
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.root.update()
    
    def clear_status(self):
        """Xóa status text box"""
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", tk.END)
        self.status_text.config(state="disabled")
    
    def trim_video(self):
        """Thực hiện cắt video"""
        self.clear_status()

        # Kiểm tra các input cơ bản
        if not self.input_file.get():
            self.add_status("❌ Lỗi: Vui lòng chọn file input")
            messagebox.showerror("Lỗi", "Vui lòng chọn file input")
            return

        if not self.output_folder.get():
            self.add_status("❌ Lỗi: Vui lòng chọn folder output")
            messagebox.showerror("Lỗi", "Vui lòng chọn folder output")
            return

        if not os.path.exists(self.input_file.get()):
            self.add_status(f"❌ Lỗi: File input không tồn tại: {self.input_file.get()}")
            messagebox.showerror("Lỗi", "File input không tồn tại")
            return

        if not os.path.exists(self.output_folder.get()):
            self.add_status(f"❌ Lỗi: Folder output không tồn tại: {self.output_folder.get()}")
            messagebox.showerror("Lỗi", "Folder output không tồn tại")
            return

        # Kiểm tra format timecode
        if not self.validate_timecode(self.timecode_in.get()):
            self.add_status("❌ Lỗi: Time Code In không đúng định dạng (hh:mm:ss)")
            messagebox.showerror("Lỗi", "Time Code In phải là hh:mm:ss\nVí dụ: 00:00:30")
            return

        if not self.validate_timecode(self.timecode_out.get()):
            self.add_status("❌ Lỗi: Time Code Out không đúng định dạng (hh:mm:ss)")
            messagebox.showerror("Lỗi", "Time Code Out phải là hh:mm:ss\nVí dụ: 00:01:10")
            return

        # Kiểm tra Time Code In phải nhỏ hơn Time Code Out
        timecode_in_sec = self.timecode_to_seconds(self.timecode_in.get())
        timecode_out_sec = self.timecode_to_seconds(self.timecode_out.get())

        if timecode_in_sec >= timecode_out_sec:
            self.add_status("❌ Lỗi: Time Code In phải nhỏ hơn Time Code Out")
            messagebox.showerror("Lỗi", f"Time Code In ({self.timecode_in.get()}) phải nhỏ hơn Time Code Out ({self.timecode_out.get()})")
            return

        # Lấy duration của file
        self.add_status("⏳ Đang kiểm tra độ dài file...")
        duration = self.get_video_duration(self.input_file.get())

        if duration is not None:
            self.add_status(f"✓ Duration: {self.seconds_to_timecode(duration)}")

            # Kiểm tra timecode không vượt quá duration
            if timecode_out_sec > duration:
                self.add_status(f"❌ Lỗi: Time Code Out ({self.timecode_out.get()}) vượt quá duration của file ({self.seconds_to_timecode(duration)})")
                messagebox.showerror("Lỗi", f"Time Code Out ({self.timecode_out.get()}) vượt quá duration của file ({self.seconds_to_timecode(duration)})")
                return

            if timecode_in_sec > duration:
                self.add_status(f"❌ Lỗi: Time Code In ({self.timecode_in.get()}) vượt quá duration của file ({self.seconds_to_timecode(duration)})")
                messagebox.showerror("Lỗi", f"Time Code In ({self.timecode_in.get()}) vượt quá duration của file ({self.seconds_to_timecode(duration)})")
                return
        else:
            self.add_status("⚠ Cảnh báo: Không thể lấy duration file, sẽ tiếp tục với các giá trị được nhập")

        # Tạo file output, tránh trùng tên bằng cách thêm suffix nếu cần
        input_filename = os.path.basename(self.input_file.get())
        name, ext = os.path.splitext(input_filename)
        base_output_filename = f"{name}_trim{ext}"
        output_path = os.path.join(self.output_folder.get(), base_output_filename)
        suffix = 1
        while os.path.exists(output_path):
            output_filename = f"{name}_trim_{suffix}{ext}"
            output_path = os.path.join(self.output_folder.get(), output_filename)
            suffix += 1

        # Xây dựng lệnh ffmpeg
        command = [
            self.ffmpeg_path,
            "-i", self.input_file.get(),
            "-ss", self.timecode_in.get(),
            "-to", self.timecode_out.get(),
            "-c", "copy",
            output_path
        ]

        # Hiển thị lệnh
        self.add_status("=" * 80)
        self.add_status("🔧 Lệnh FFmpeg hoàn chỉnh:")
        self.add_status("=" * 80)
        command_str = " ".join(command)
        self.add_status(command_str)
        self.add_status("=" * 80)
        self.add_status("")
        self.add_status("⏳ Đang xử lý... Vui lòng chờ")

        # Chạy ffmpeg trong thread riêng để không block UI
        thread = threading.Thread(target=self.run_ffmpeg, args=(command, output_path))
        thread.start()
    
    def run_ffmpeg(self, command, output_path):
        """Chạy lệnh ffmpeg"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in process.stdout:
                self.add_status(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.add_status("")
                self.add_status("✅ Thành công! File đã được cắt:")
                self.add_status(output_path)
                messagebox.showinfo("Thành công", f"Cắt file thành công!\n\n{output_path}")
            else:
                self.add_status("")
                self.add_status(f"❌ Lỗi: FFmpeg trả về mã lỗi {process.returncode}")
                messagebox.showerror("Lỗi", f"FFmpeg lỗi: {process.returncode}")
        
        except FileNotFoundError:
            self.add_status("")
            self.add_status(f"❌ Lỗi: Không tìm thấy ffmpeg tại: {self.ffmpeg_path}")
            self.add_status("Vui lòng đảm bảo ffmpeg.exe nằm trong thư mục gốc của chương trình")
            messagebox.showerror("Lỗi", f"Không tìm thấy ffmpeg tại: {self.ffmpeg_path}")
        
        except Exception as e:
            self.add_status("")
            self.add_status(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

def main():
    root = tk.Tk()
    app = FFmpegTrimmerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()