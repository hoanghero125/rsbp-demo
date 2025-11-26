# QUICK FIX: User Service Exit Code 216/GROUP

## 🔴 Vấn Đề

Service không start được, lỗi:
```
status=216/GROUP
Failed with result 'exit-code'
```

## 🎯 Nguyên Nhân

Service file có `User=pi` và `Group=pi`, nhưng **user service không được phép chỉ định User/Group**!

User service tự động chạy với user của nó rồi.

## ✅ Giải Pháp Nhanh

### Cách 1: Dùng File Mới (Khuyến Nghị)

```bash
# 1. Stop service hiện tại
systemctl --user stop disability-support.service

# 2. Xóa service cũ
rm ~/.config/systemd/user/disability-support.service

# 3. Copy file MỚI (disability-support-user.service)
cp ~/rsbp-demo/disability-support-user.service ~/.config/systemd/user/disability-support.service

# 4. Reload
systemctl --user daemon-reload

# 5. Start lại
systemctl --user start disability-support.service

# 6. Kiểm tra
systemctl --user status disability-support.service
```

### Cách 2: Sửa File Thủ Công

```bash
# 1. Stop service
systemctl --user stop disability-support.service

# 2. Sửa file
nano ~/.config/systemd/user/disability-support.service
```

**XÓA 2 dòng này:**
```ini
User=pi
Group=pi
```

**SỬA dòng WantedBy từ:**
```ini
WantedBy=multi-user.target
```

**THÀNH:**
```ini
WantedBy=default.target
```

**Lưu file (Ctrl+O, Enter, Ctrl+X)**

```bash
# 3. Reload
systemctl --user daemon-reload

# 4. Start lại
systemctl --user start disability-support.service

# 5. Kiểm tra
systemctl --user status disability-support.service
```

## ✅ Kiểm Tra Thành Công

Sau khi fix, bạn sẽ thấy:

```
● disability-support.service - Disability Support System
     Loaded: loaded
     Active: active (running)  ← QUAN TRỌNG: active (running)!
     Main PID: 1234
```

**KHÔNG còn:**
- ❌ `activating (auto-restart)`
- ❌ `status=216/GROUP`
- ❌ `Failed with result 'exit-code'`

## 📊 So Sánh Service File

### ❌ System Service (disability-support.service)
```ini
[Service]
User=pi        # ← CẦN khi dùng system service
Group=pi       # ← CẦN khi dùng system service
...

[Install]
WantedBy=multi-user.target
```

### ✅ User Service (disability-support-user.service)
```ini
[Service]
# KHÔNG có User=
# KHÔNG có Group=
...

[Install]
WantedBy=default.target
```

## 🧪 Test Hoàn Chỉnh

```bash
# 1. Kiểm tra status
systemctl --user status disability-support.service

# 2. Xem logs
journalctl --user -u disability-support.service -f

# 3. Test reboot
sudo reboot
```

Sau reboot:
```bash
# Kiểm tra service tự động chạy
systemctl --user status disability-support.service
```

## 🔧 Nếu Vẫn Lỗi

### Xem Logs Chi Tiết:

```bash
journalctl --user -u disability-support.service -n 50
```

### Kiểm Tra File Path:

```bash
# File python3 phải tồn tại
ls -la /home/pi/rsbp-demo/venv/bin/python3

# File main.py phải tồn tại
ls -la /home/pi/rsbp-demo/main.py

# Venv phải có dependencies
source /home/pi/rsbp-demo/venv/bin/activate
python3 -c "import config; print('OK')"
```

### Test Chạy Thủ Công:

```bash
# Trong venv
cd ~/rsbp-demo
source venv/bin/activate
python3 main.py
```

Nếu chạy thủ công OK → vấn đề là service file.
Nếu chạy thủ công lỗi → vấn đề là code/dependencies.

## ✅ Kết Luận

- ✅ Dùng `disability-support-user.service` cho user service
- ✅ KHÔNG có `User=` và `Group=` trong user service
- ✅ `WantedBy=default.target` cho user service
- ✅ Quản lý bằng `systemctl --user` (không có sudo)

**Chạy Cách 1 ở trên để fix ngay!** 🚀
