# Hướng Dẫn Tự Động Chạy Khi Khởi Động

Tài liệu này hướng dẫn cách cấu hình hệ thống tự động chạy khi Raspberry Pi khởi động.

## 📋 Tổng Quan

Sử dụng **systemd service** để:
- Tự động chạy `main.py` khi Pi khởi động
- Tự động restart nếu chương trình bị lỗi
- Quản lý dễ dàng (start/stop/restart)
- Xem logs tập trung

## 🚀 Cài Đặt Tự Động Khởi Động

### Bước 1: Copy Service File

```bash
# Copy service file vào systemd
sudo cp disability-support.service /etc/systemd/system/

# Reload systemd để nhận service mới
sudo systemctl daemon-reload
```

### Bước 2: Enable Service (Tự động chạy khi boot)

```bash
# Enable service để chạy khi khởi động
sudo systemctl enable disability-support.service

# Kiểm tra status
sudo systemctl status disability-support.service
```

### Bước 3: Start Service Ngay

```bash
# Khởi động service ngay lập tức (không cần reboot)
sudo systemctl start disability-support.service

# Kiểm tra service đã chạy chưa
sudo systemctl status disability-support.service
```

## 🎛️ Quản Lý Service

### Các Lệnh Cơ Bản

```bash
# Xem trạng thái
sudo systemctl status disability-support.service

# Khởi động service
sudo systemctl start disability-support.service

# Dừng service
sudo systemctl stop disability-support.service

# Restart service
sudo systemctl restart disability-support.service

# Disable auto-start (không tự động chạy khi boot nữa)
sudo systemctl disable disability-support.service
```

### Xem Logs Real-time

```bash
# Xem logs của service
sudo journalctl -u disability-support.service -f

# Xem logs từ lần boot gần nhất
sudo journalctl -u disability-support.service -b

# Xem 100 dòng logs cuối
sudo journalctl -u disability-support.service -n 100
```

## 🔍 Kiểm Tra Service Hoạt Động

### 1. Kiểm Tra Status

```bash
sudo systemctl status disability-support.service
```

**Output mong đợi:**
```
● disability-support.service - Disability Support System
     Loaded: loaded (/etc/systemd/system/disability-support.service; enabled)
     Active: active (running) since ...
```

- **Loaded**: Service đã được tải
- **enabled**: Sẽ tự động chạy khi boot
- **Active: active (running)**: Đang chạy

### 2. Xem Logs

```bash
sudo journalctl -u disability-support.service -f
```

Bạn sẽ thấy logs giống như khi chạy `python3 main.py` thủ công:
```
System is ready and running
Press the button to start recording
```

### 3. Test Reboot

```bash
# Reboot Raspberry Pi
sudo reboot
```

Sau khi Pi khởi động lại:
- Chương trình sẽ **tự động chạy**
- Bạn có thể nhấn nút để test ngay

## ⚙️ Service File Giải Thích

```ini
[Unit]
Description=Disability Support System
After=network.target sound.target  # Đợi network và sound khởi động trước

[Service]
Type=simple
User=pi                            # Chạy với user pi
Group=pi
WorkingDirectory=/home/pi/rsbp-demo  # Thư mục làm việc
Environment="PATH=..."             # PATH bao gồm venv
Environment="API_KEY=..."          # API key cho LLM
ExecStart=.../venv/bin/python3 .../main.py  # Lệnh chạy
Restart=always                     # Tự động restart nếu crash
RestartSec=10                      # Đợi 10s trước khi restart
StandardOutput=journal             # Logs vào journald
StandardError=journal

[Install]
WantedBy=multi-user.target         # Enable với multi-user target
```

## 🛠️ Troubleshooting

### Service Không Start

```bash
# Xem chi tiết lỗi
sudo journalctl -u disability-support.service -n 50

# Kiểm tra syntax service file
sudo systemd-analyze verify /etc/systemd/system/disability-support.service
```

### Sửa Service File

```bash
# 1. Stop service
sudo systemctl stop disability-support.service

# 2. Sửa file trong project
nano disability-support.service

# 3. Copy lại
sudo cp disability-support.service /etc/systemd/system/

# 4. Reload và restart
sudo systemctl daemon-reload
sudo systemctl restart disability-support.service
```

### Service Không Tự Động Chạy Sau Reboot

```bash
# Kiểm tra service đã enabled chưa
sudo systemctl is-enabled disability-support.service
# Nếu hiển thị "disabled", chạy:
sudo systemctl enable disability-support.service
```

### GPIO Permission Issues

Nếu gặp lỗi GPIO permission:
```bash
# Thêm user vào gpio group
sudo usermod -a -G gpio pi

# Logout và login lại, hoặc reboot
sudo reboot
```

## 🔐 Bảo Mật

### Không Hardcode API Key trong Service File

**Khuyến nghị:** Sử dụng file `.env` thay vì Environment trong service file.

**Cách 1: Sử dụng EnvironmentFile**

```ini
[Service]
EnvironmentFile=/home/pi/rsbp-demo/.env
```

Trong `.env`:
```bash
API_KEY=http://203.162.88.105/pvlm-api
```

**Cách 2: Load từ code** (đã implement với python-dotenv)

Xóa dòng `Environment="API_KEY=..."` trong service file, code sẽ tự load từ `.env`.

## 📝 Kiểm Tra Hoàn Chỉnh

### Checklist Trước Khi Enable

- [ ] Service file đã copy vào `/etc/systemd/system/`
- [ ] `daemon-reload` đã chạy
- [ ] Venv đã được tạo và có đủ dependencies
- [ ] `.env` file có API_KEY đúng
- [ ] Test chạy thủ công thành công (`python3 main.py`)
- [ ] Hardware (button, camera, micro, loa) hoạt động

### Test Quy Trình

1. **Enable và Start:**
   ```bash
   sudo systemctl enable disability-support.service
   sudo systemctl start disability-support.service
   ```

2. **Kiểm tra logs:**
   ```bash
   sudo journalctl -u disability-support.service -f
   ```

3. **Test hardware:**
   - Nhấn button → Ghi âm
   - Nhấn button lần 2 → Xử lý và phát âm thanh

4. **Test reboot:**
   ```bash
   sudo reboot
   ```

5. **Sau reboot, kiểm tra:**
   ```bash
   sudo systemctl status disability-support.service
   ```

## 📊 Monitoring

### Xem Resource Usage

```bash
# CPU và Memory usage
systemctl status disability-support.service

# Chi tiết process
ps aux | grep main.py
```

### Kiểm Tra Uptime

```bash
# Thời gian service đã chạy
sudo systemctl status disability-support.service | grep Active
```

## 🔄 Updates và Maintenance

### Update Code

```bash
# 1. Stop service
sudo systemctl stop disability-support.service

# 2. Pull code mới
cd /home/pi/rsbp-demo
git pull

# 3. Update dependencies nếu cần
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart service
sudo systemctl start disability-support.service
```

### Backup Logs

```bash
# Export logs ra file
sudo journalctl -u disability-support.service > ~/disability-support-logs.txt
```

## ✅ Kết Luận

Sau khi setup xong, hệ thống sẽ:
- ✅ Tự động chạy khi Raspberry Pi khởi động
- ✅ Tự động restart nếu gặp lỗi
- ✅ Logs tập trung, dễ kiểm tra
- ✅ Quản lý dễ dàng với systemctl

**Chạy một lần, sử dụng mãi mãi!** 🎉
