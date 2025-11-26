# Fix Audio Khi Chạy Qua Systemd

## 🎯 Vấn Đề

- ✅ Chạy thủ công `python3 main.py` → Có tiếng
- ❌ Chạy qua systemd `systemctl start disability-support` → KHÔNG có tiếng

## 🔍 Nguyên Nhân

**Systemd system service** chạy trong **system context**, không có quyền truy cập audio session của user. Audio devices (ALSA/PulseAudio) yêu cầu chạy trong user session.

## ✅ Giải Pháp: Dùng User Service

Thay vì dùng **system service** (`/etc/systemd/system/`), ta dùng **user service** (`~/.config/systemd/user/`).

### Ưu Điểm User Service:
- ✅ Chạy trong user session → Có quyền audio tự nhiên
- ✅ Không cần sudo để quản lý
- ✅ Tự động start khi user login
- ✅ Dừng khi user logout (tuỳ chọn)

---

## 🚀 Cài Đặt User Service

### Bước 1: Tạo Thư Mục User Service

```bash
# Tạo thư mục cho user services
mkdir -p ~/.config/systemd/user/
```

### Bước 2: Copy Service File

```bash
# Copy service file vào user systemd directory
cp ~/rsbp-demo/disability-support.service ~/.config/systemd/user/

# Reload user systemd
systemctl --user daemon-reload
```

### Bước 3: Enable User Service

```bash
# Enable service (tự động chạy khi login)
systemctl --user enable disability-support.service

# Start service ngay
systemctl --user start disability-support.service
```

### Bước 4: Enable Linger (Quan Trọng!)

**Linger** cho phép service chạy ngay cả khi chưa login:

```bash
# Enable linger cho user pi
sudo loginctl enable-linger pi

# Kiểm tra linger
loginctl show-user pi | grep Linger
# Output: Linger=yes
```

### Bước 5: Kiểm Tra

```bash
# Xem status
systemctl --user status disability-support.service

# Xem logs
journalctl --user -u disability-support.service -f
```

---

## 🔄 Cleanup: Xóa System Service (Nếu Đã Cài)

Nếu bạn đã cài system service trước đó, xóa nó đi:

```bash
# Stop và disable system service
sudo systemctl stop disability-support.service
sudo systemctl disable disability-support.service

# Xóa file
sudo rm /etc/systemd/system/disability-support.service

# Reload
sudo systemctl daemon-reload
```

---

## 🎛️ Quản Lý User Service

### Các Lệnh Cơ Bản

```bash
# Xem status
systemctl --user status disability-support.service

# Start
systemctl --user start disability-support.service

# Stop
systemctl --user stop disability-support.service

# Restart
systemctl --user restart disability-support.service

# Enable (tự động chạy)
systemctl --user enable disability-support.service

# Disable (không tự động chạy)
systemctl --user disable disability-support.service
```

### Xem Logs

```bash
# Real-time logs
journalctl --user -u disability-support.service -f

# 100 dòng cuối
journalctl --user -u disability-support.service -n 100

# Từ lần boot gần nhất
journalctl --user -u disability-support.service -b
```

---

## 🧪 Test Sau Khi Setup

### 1. Kiểm Tra Service Running

```bash
systemctl --user status disability-support.service
```

**Mong đợi:**
```
● disability-support.service - Disability Support System
     Loaded: loaded
     Active: active (running)
```

### 2. Test Button

- Nhấn button lần 1 → Ghi âm
- Nói câu hỏi
- Nhấn button lần 2 → Xử lý
- **Nghe audio phát ra từ loa** ✅

### 3. Test Reboot

```bash
sudo reboot
```

Sau khi Pi boot xong:
- Service tự động chạy (do enable-linger)
- Test button ngay để kiểm tra audio

---

## 🔧 Troubleshooting

### Service Không Start

```bash
# Xem logs chi tiết
journalctl --user -u disability-support.service -n 50

# Kiểm tra file service
systemctl --user cat disability-support.service
```

### Vẫn Không Có Audio

#### 1. Kiểm tra user trong audio group:

```bash
groups pi
```

Nếu không có `audio`, thêm vào:

```bash
sudo usermod -a -G audio pi
# Sau đó logout/login hoặc reboot
```

#### 2. Kiểm tra PulseAudio:

```bash
# Kiểm tra PulseAudio running
ps aux | grep pulseaudio

# Restart PulseAudio
pulseaudio -k
pulseaudio --start
```

#### 3. Test audio thủ công:

```bash
# Trong user session
aplay ~/rsbp-demo/audio/test_tts_output.wav
```

### Service Không Tự Động Start Sau Reboot

Kiểm tra linger:

```bash
loginctl show-user pi | grep Linger
```

Nếu không phải `Linger=yes`:

```bash
sudo loginctl enable-linger pi
```

---

## 📝 So Sánh System vs User Service

| Feature | System Service | User Service |
|---------|---------------|--------------|
| Quyền audio | ❌ Không có | ✅ Có |
| Quản lý | Cần sudo | Không cần sudo |
| Chạy khi | Boot | User login (với linger: boot) |
| Context | System | User session |
| Logs | `sudo journalctl` | `journalctl --user` |

---

## ✅ Kết Luận

Sau khi chuyển sang **user service** + **enable linger**:

- ✅ Audio hoạt động khi chạy qua systemd
- ✅ Tự động start khi Pi boot
- ✅ Không cần sudo để quản lý
- ✅ Có đầy đủ quyền audio trong user session

**Giải pháp hoàn hảo!** 🎉
