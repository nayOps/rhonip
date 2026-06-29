"""
Module pour lecteur d'empreintes digitales
Supporte communication USB directe et libfprint
"""

from .usb_reader import USBFingerprintReader
from .serial_reader import SerialFingerprintReader
from .matcher import FingerprintMatcher

__all__ = ['USBFingerprintReader', 'SerialFingerprintReader', 'FingerprintMatcher']

