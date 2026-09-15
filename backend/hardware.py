from abc import ABC, abstractmethod
import serial
import time
import os
import logging

# Configure hardware logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrailSenseHW")

class HardwareInterface(ABC):
    @abstractmethod
    def set_led(self, color: str):
        """
        Set the status LED color.
        Args:
            color: 'RED', 'GREEN', 'AMBER', or 'OFF'
        """
        pass

class LocalHardware(HardwareInterface):
    """
    Simulation interface for local development when no hardware is attached.
    """
    def set_led(self, color: str):
        logger.info(f"HARDWARE_SIM: LED set to {color}")

class ArduinoSerialHardware(HardwareInterface):
    """
    Production interface for the Arduino Uno Q via internal UART or USB Serial.
    """
    def __init__(self, port='/dev/ttyMSM0', baud=9600):
        self.port = port
        self.baud = baud
        self.ser = None
        self.connect()

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            logger.info(f"Connected to Hardware Bridge at {self.port}")
        except Exception as e:
            logger.error(f"Hardware Bridge Connection Failed: {e}")
            self.ser = None

    def set_led(self, color: str):
        if not self.ser: return
        
        # Protocol: Single byte command
        command_map = {
            'RED': b'R',
            'GREEN': b'G',
            'AMBER': b'A',
            'OFF': b'O'
        }
        
        cmd = command_map.get(color, b'O')
        
        try:
            self.ser.write(cmd + b'\n')
        except Exception as e:
            logger.error(f"Serial Transmission Error: {e}")

def get_hardware() -> HardwareInterface:
    """
    Factory to return the appropriate hardware interface based on environment.
    """
    if os.environ.get("TRAILSENSE_HW") == "SERIAL":
        return ArduinoSerialHardware()
    return LocalHardware()
