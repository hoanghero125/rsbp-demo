# Hướng Dẫn Sử Dụng LED - ReSpeaker 2-Mics HAT

Tài liệu này mô tả cách sử dụng 3 đèn LED RGB APA102 trên ReSpeaker 2-Mics HAT để hiển thị trạng thái hệ thống.

## 📋 Tổng Quan

### Hardware
- **3 đèn LED RGB APA102** trên board ReSpeaker 2-Mics HAT
- Mỗi LED có thể hiển thị **16 triệu màu** (RGB: 0-255 cho mỗi kênh)
- Điều khiển qua **SPI interface**

### Tính Năng
- Hiển thị trạng thái hệ thống bằng màu sắc khác nhau
- Animation (xoay, nhấp nháy, pulsing) cho một số trạng thái
- Chạy trong background thread, không làm gián đoạn pipeline chính

---

## 🎨 Màu Sắc và Trạng Thái

| Trạng Thái | Màu Sắc | Hiệu Ứng | Mô Tả |
|-----------|---------|----------|-------|
| **IDLE** | 🟢 Xanh lá | Solid | Đang chờ người dùng nhấn nút |
| **RECORDING** | 🔴 Đỏ | Solid | Đang ghi âm |
| **CAPTURING** | 🟡 Vàng | Solid | Đang chụp ảnh |
| **PROCESSING** | 🔵 Cyan | Rotating | Đang xử lý (STT → VLM → TTS) |
| **SPEAKING** | 🔵 Xanh dương | Pulsing | Đang phát audio |
| **ERROR** | 🔴 Đỏ | Blinking | Lỗi hệ thống |

### Giải Thích Chi Tiết:

#### 🟢 IDLE (Xanh lá)
- Hệ thống sẵn sàng, chờ người dùng nhấn nút
- Tất cả 3 LED sáng xanh lá đồng thời

#### 🔴 RECORDING (Đỏ)
- Đang ghi âm câu hỏi từ người dùng
- Tất cả 3 LED sáng đỏ đồng thời
- Bắt đầu khi nhấn nút lần 1

#### 🟡 CAPTURING (Vàng)
- Đang chụp ảnh để gửi cho VLM
- Tất cả 3 LED sáng vàng đồng thời
- Xảy ra sau khi dừng ghi âm

#### 🔵 PROCESSING (Cyan - Xoay)
- Đang xử lý dữ liệu (STT → VLM → TTS)
- **Hiệu ứng xoay**: 1 LED cyan sáng, di chuyển từ LED 0 → 1 → 2 → 0...
- Thời gian: Tùy thuộc vào tốc độ API

#### 🔵 SPEAKING (Xanh dương - Nhấp nháy)
- Đang phát audio trả lời cho người dùng
- **Hiệu ứng pulsing**: Tất cả LED xanh dương, độ sáng tăng giảm liên tục
- Tạo cảm giác "thở" (breathing effect)

#### 🔴 ERROR (Đỏ - Nhấp nháy)
- Lỗi hệ thống (STT failed, VLM failed, TTS failed, etc.)
- **Hiệu ứng nhấp nháy**: Sáng → Tắt → Sáng (0.3s mỗi lần)
- Sau 2s sẽ tự động quay về IDLE

---

## 🚀 Cài Đặt

### Bước 1: Bật SPI Interface

LED điều khiển qua SPI, cần bật SPI trên Raspberry Pi:

```bash
# Mở raspi-config
sudo raspi-config

# Chọn: Interfacing Options → SPI → Yes
# Hoặc chạy lệnh trực tiếp:
sudo raspi-config nonint do_spi 0
```

**Reboot sau khi bật SPI:**
```bash
sudo reboot
```

**Kiểm tra SPI đã bật:**
```bash
ls /dev/spi*
# Output mong đợi: /dev/spidev0.0  /dev/spidev0.1
```

### Bước 2: Cài Đặt Thư Viện

```bash
# Activate venv
cd ~/rsbp-demo
source venv/bin/activate

# Cài đặt apa102-pi library
pip install apa102-pi
```

**Lưu ý:** `apa102-pi` đã được thêm vào `requirements.txt`, nên bạn có thể cài tất cả dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧪 Kiểm Tra LED

### Test 1: Chạy Test Script Độc Lập

```bash
cd ~/rsbp-demo
source venv/bin/activate

# Chạy test LED
python3 led_controller.py
```

**Output mong đợi:**
```
Testing LED Controller...
LED initialized successfully
Testing LEDs...
  Testing color: RED
  Testing color: GREEN
  Testing color: BLUE
  Testing color: YELLOW
  Testing color: CYAN
  Testing color: PURPLE
  Testing color: WHITE
  Testing individual LEDs
LED test complete
Testing IDLE state...
Testing RECORDING state...
Testing CAPTURING state...
Testing PROCESSING state...
Testing SPEAKING state...
Testing ERROR state...
Test complete!
```

**Quan sát:**
- Mỗi màu sẽ sáng 0.5s
- Từng LED sáng riêng lẻ (test individual LEDs)
- Các trạng thái sẽ hiển thị với animation

### Test 2: Kiểm Tra Trong Hệ Thống

```bash
# Chạy main.py và quan sát LED thay đổi
python3 main.py
```

**Quy trình test:**
1. Khởi động → LED **xanh lá** (IDLE)
2. Nhấn nút → LED **đỏ** (RECORDING)
3. Nói câu hỏi
4. Nhấn nút lần 2 → LED **vàng** (CAPTURING) → LED **cyan xoay** (PROCESSING)
5. Chờ xử lý → LED **xanh dương nhấp nháy** (SPEAKING)
6. Kết thúc → LED **xanh lá** (IDLE)

---

## 🔧 Tùy Chỉnh

### Thay Đổi Màu Sắc

Trong `led_controller.py`, sửa dictionary `COLORS`:

```python
COLORS = {
    'OFF': (0, 0, 0),
    'GREEN': (0, 255, 0),      # IDLE
    'RED': (255, 0, 0),        # RECORDING / ERROR
    'YELLOW': (255, 255, 0),   # CAPTURING
    'CYAN': (0, 255, 255),     # PROCESSING
    'BLUE': (0, 0, 255),       # SPEAKING
    'PURPLE': (128, 0, 128),   # Alternative
    'WHITE': (255, 255, 255),  # System ready
}
```

**Ví dụ:** Đổi IDLE từ xanh lá sang xanh dương:
```python
def show_idle(self):
    """Display IDLE state - solid blue."""
    logger.debug("LED: IDLE (Blue)")
    self.set_all_leds(self.COLORS['BLUE'])
```

### Thay Đổi Độ Sáng

Trong `led_controller.py`, method `initialize()`:

```python
self.strip = APA102(num_led=self.num_leds,
                   global_brightness=10,  # ← Thay đổi: 0-31 (10 = vừa phải)
                   order='rgb')
```

- `0` = Tối nhất
- `31` = Sáng nhất
- `10` = Mức vừa phải (khuyến nghị)

### Thay Đổi Tốc Độ Animation

#### Processing (Rotating):
```python
def _animate_processing(self):
    # ...
    time.sleep(0.2)  # ← Giảm = xoay nhanh hơn, tăng = xoay chậm hơn
```

#### Speaking (Pulsing):
```python
def _animate_speaking(self):
    brightness_levels = list(range(0, 256, 15)) + list(range(255, -1, -15))
    # ← Thay 15 thành 30 = pulsing nhanh hơn
    # ...
    time.sleep(0.03)  # ← Giảm = pulsing mượt hơn
```

#### Error (Blinking):
```python
def _animate_error(self):
    # ...
    time.sleep(0.3)  # ← Tốc độ nhấp nháy
```

---

## 🛠️ Troubleshooting

### LED Không Sáng

#### 1. Kiểm tra SPI đã bật chưa:
```bash
ls /dev/spi*
```
Nếu không có output → SPI chưa bật → Xem **Bước 1: Bật SPI Interface**

#### 2. Kiểm tra apa102 library:
```bash
source venv/bin/activate
python3 -c "import apa102; print('OK')"
```
Nếu lỗi → Cài lại: `pip install apa102-pi`

#### 3. Kiểm tra quyền truy cập SPI:
```bash
groups pi
```
Nên có `spi` trong list. Nếu không:
```bash
sudo usermod -a -G spi pi
# Logout/login hoặc reboot
```

#### 4. Test thủ công:
```bash
python3 led_controller.py
```
Xem logs để tìm lỗi cụ thể.

### LED Sáng Nhưng Màu Sai

- Kiểm tra `order='rgb'` trong `APA102()` initialization
- Thử đổi thành `order='bgr'` nếu màu sắc bị đảo

### LED Quá Sáng / Quá Tối

- Điều chỉnh `global_brightness` (0-31) trong `initialize()`

### Animation Không Chạy

- Kiểm tra logs: `journalctl --user -u disability-support.service -n 50`
- Đảm bảo không có Exception trong animation thread

### LED Không Tắt Khi Shutdown

```bash
# Tắt thủ công
python3 -c "from apa102 import APA102; strip = APA102(3); strip.clear_strip(); strip.cleanup()"
```

---

## 📊 Luồng Hoạt Động LED

```
System Start
    ↓
[Initialize] → Test all colors → Test states
    ↓
🟢 IDLE (Green) - Waiting for button press
    ↓
Button Press #1
    ↓
🔴 RECORDING (Red) - Recording audio
    ↓
Button Press #2
    ↓
🟡 CAPTURING (Yellow) - Taking photo
    ↓
🔵 PROCESSING (Rotating Cyan) - STT → VLM → TTS
    ↓
🔵 SPEAKING (Pulsing Blue) - Playing audio
    ↓
🟢 IDLE (Green) - Ready for next query
```

**Nếu có lỗi ở bất kỳ bước nào:**
```
❌ ERROR (Blinking Red) → 2 seconds → 🟢 IDLE
```

---

## 💡 Ví Dụ Sử Dụng LED Controller

### Ví Dụ 1: Sử Dụng Trong Code

```python
from led_controller import LEDController

# Initialize
led = LEDController(num_leds=3)
if led.initialize():
    # Set state
    led.set_state(LEDController.STATE_IDLE)

    # Do something...
    led.set_state(LEDController.STATE_PROCESSING)

    # Clean up when done
    led.cleanup()
```

### Ví Dụ 2: Tùy Chỉnh Màu Sắc

```python
# Set all LEDs to custom color (R, G, B)
led.set_all_leds((255, 128, 0))  # Orange

# Set individual LED
led.set_led(0, (255, 0, 0))    # LED 0 = Red
led.set_led(1, (0, 255, 0))    # LED 1 = Green
led.set_led(2, (0, 0, 255))    # LED 2 = Blue
```

### Ví Dụ 3: Test Animation

```python
led = LEDController(num_leds=3)
led.initialize()

# Test processing animation (5 seconds)
led.set_state(LEDController.STATE_PROCESSING)
time.sleep(5)

# Test speaking animation (5 seconds)
led.set_state(LEDController.STATE_SPEAKING)
time.sleep(5)

led.cleanup()
```

---

## 📚 Tài Liệu Tham Khảo

### ReSpeaker 2-Mics HAT
- **Wiki**: [Seeed Studio ReSpeaker 2-Mics HAT](https://wiki.seeedstudio.com/respeaker_2_mics_pi_hat_raspberry_v2/)
- **GitHub**: [respeaker/mic_hat](https://github.com/respeaker/mic_hat)

### APA102 LED Library
- **GitHub**: [tinue/apa102-pi](https://github.com/tinue/apa102-pi)
- **PyPI**: [apa102-pi](https://pypi.org/project/apa102-pi/)

### SPI Interface
- **Raspberry Pi Documentation**: [SPI](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#spi-overview)

---

## ✅ Checklist Setup LED

- [ ] SPI interface đã bật (`ls /dev/spi*`)
- [ ] apa102-pi library đã cài (`pip list | grep apa102`)
- [ ] User pi trong group spi (`groups pi`)
- [ ] Test LED thành công (`python3 led_controller.py`)
- [ ] LED hoạt động trong main.py
- [ ] LED tự động chạy qua systemd user service

---

## 🎯 Kết Luận

Với hệ thống LED:
- ✅ Người dùng **nhìn thấy trạng thái** hệ thống ngay lập tức
- ✅ **Dễ dàng debug** khi có lỗi (LED đỏ nhấp nháy)
- ✅ **Trực quan** và **chuyên nghiệp**
- ✅ **Không ảnh hưởng** đến hiệu suất pipeline chính

Hệ thống Disability Support hoàn chỉnh với **feedback thị giác**! 🎨✨
