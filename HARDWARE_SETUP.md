
# TrailSense - Hardware Configuration

This guide explains how to deploy the TrailSense system on the Arduino Uno Q (or similar Linux-based boards) and connect the ESP32-CAM.

## Hardware Setup

1.  **ESP32-CAM**:
    - Flash the "CameraWebServer" example sketch (available in Arduino IDE Examples).
    - Connect to the same WiFi network as the Uno Q.
    - Note the IP address (e.g., `192.168.1.105`).

2.  **Arduino Uno Q (Linux/Reader Side)**:
    - This project runs on the Linux environment of the board.
    - **Connect LEDs**:
        - Green LED -> GPIO Pin X (Logic dependent on MCU bridge)
        - Red LED -> GPIO Pin Y
    - **Install Dependencies**:
        ```bash
        sudo apt-get update && sudo apt-get install python3-opencv python3-pip
        pip3 install fastapi uvicorn requests pyserial
        ```

3.  **Deploy Code**:
    - Copy the `backend/` folder to the board.
    - Run: `CAMERA_SOURCE="http://<ESP32_IP>:81/stream" TRAILSENSE_HW="SERIAL" python3 main.py`

## Software Configuration

- **Mock Mode (Laptop)**:
    - Simply run `python main.py` (uses Webcam 0).
- **Production Mode (Board)**:
    - Set environment variables:
        - `CAMERA_SOURCE`: URL of ESP32 stream.
        - `TRAILSENSE_HW`: Set to `SERIAL` to enable hardware LED control via serial bridge.

## Architecture

- `backend/hardware.py`: Handles communication with the board's MCU/GPIOs. Modify `ArduinoSerialHardware` if your board uses generic GPIOs via `sysfs` or `libgpiod` instead of Serial.
- `backend/vision_core.py`: Logic engine. Agnostic to hardware.
