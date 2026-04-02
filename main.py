from pynput import keyboard, mouse
import ctypes
from ctypes import wintypes
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QTextOption, QFontMetrics, QIcon, QPainter, QColor, QPen, QBrush, QLinearGradient
from PySide6.QtCore import Qt, QFileInfo, QDir, QSettings, QRectF
import sys
from collections import deque

class Keyinput:
	def __init__(self):
		self.pressed_keys = set()
		self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
		self.listener.start()
	
	def on_press(self, key):
		try:
			self.pressed_keys.add(key.char)
		except AttributeError:
			self.pressed_keys.add(str(key))
	
	def on_release(self, key):
		try:
			self.pressed_keys.discard(key.char)
		except AttributeError:
			self.pressed_keys.discard(str(key))

user32 = ctypes.windll.user32

WM_INPUT = 0x00FF
RID_INPUT = 0x10000003
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

WM_INPUT = 0x00FF
RID_INPUT = 0x10000003

class RAWINPUTHEADER(ctypes.Structure):
	_fields_ = [
		("dwType", wintypes.DWORD),
		("dwSize", wintypes.DWORD),
		("hDevice", wintypes.HANDLE),
		("wParam", wintypes.WPARAM),
	]
class RAWMOUSE(ctypes.Structure):
	_fields_ = [
		("usFlags", wintypes.USHORT),
		("ulButtons", wintypes.ULONG),
		("ulRawButtons", wintypes.ULONG),
		("lLastX", wintypes.LONG),
		("lLastY", wintypes.LONG),
		("ulExtraInformation", wintypes.ULONG),
	]
class RAWINPUT(ctypes.Structure):
	_fields_ = [
		("header", RAWINPUTHEADER),
		("mouse", RAWMOUSE),
	]
class RAWINPUTDEVICE(ctypes.Structure):
	_fields_ = [
		("usUsagePage", wintypes.USHORT),
		("usUsage", wintypes.USHORT),
		("dwFlags", wintypes.DWORD),
		("hwndTarget", wintypes.HWND),
	]
class Mouseinput:
	def __init__(self, hwnd):
		self.dx = 0
		self.dy = 0
		self.buttons = set()
		self.scroll = 0
		rid = RAWINPUTDEVICE()
		rid.usUsagePage = 0x01
		rid.usUsage = 0x02
		rid.dwFlags = 0x00000100
		rid.hwndTarget = hwnd
		user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid))

	def handle_raw_input(self, lParam):
		size = wintypes.UINT(0)
		user32.GetRawInputData(lParam, RID_INPUT, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
		buffer = ctypes.create_string_buffer(size.value)
		user32.GetRawInputData(lParam, RID_INPUT, buffer, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
		raw = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents
		if raw.header.dwType == 0:
			mouse = raw.mouse
			self.dx += mouse.lLastX
			self.dy += mouse.lLastY
			btn = mouse.ulButtons
			if btn & 0x0001:
				self.buttons.add("left")
			if btn & 0x0002:
				self.buttons.discard("left")
			if btn & 0x0004:
				self.buttons.add("right")
			if btn & 0x0008:
				self.buttons.discard("right")
			if btn & 0x0010:
				self.buttons.add("middle")
			if btn & 0x0020:
				self.buttons.discard("middle")
			if btn & 0x0040:
				self.buttons.add("x1")
			if btn & 0x0080:
				self.buttons.discard("x1")
			if btn & 0x0100:
				self.buttons.add("x2")
			if btn & 0x0200:
				self.buttons.discard("x2")
			if btn & 0x0400:
				wheel_delta = ctypes.c_short((btn >> 16) & 0xFFFF).value
				self.scroll += wheel_delta

key_layouts = [
	[
		[("Esc", "Key.esc", 1.0), None, ("F1", "Key.f1", 1.0), ("F2", "Key.f2", 1.0), ("F3", "Key.f3", 1.0), ("F4", "Key.f4", 1.0), None, ("F5", "Key.f5", 1.0), ("F6", "Key.f6", 1.0), ("F7", "Key.f7", 1.0), ("F8", "Key.f8", 1.0), None, ("F9", "Key.f9", 1.0), ("F10", "Key.f10", 1.0), ("F11", "Key.f11", 1.0), ("F12", "Key.f12", 1.0)],
		[("半角", "Key.caps_lock", 1.0), ("1", "1", 1.0), ("2", "2", 1.0), ("3", "3", 1.0), ("4", "4", 1.0), ("5", "5", 1.0), ("6", "6", 1.0), ("7", "7", 1.0), ("8", "8", 1.0), ("9", "9", 1.0), ("0", "0", 1.0), ("-", "-", 1.0), ("^", "^", 1.0), ("\\", "\\", 1.0), ("BS", "Key.backspace", 1.0)],
		[("Tab", "Key.tab", 1.5), ("Q", "q", 1.0), ("W", "w", 1.0), ("E", "e", 1.0), ("R", "r", 1.0), ("T", "t", 1.0), ("Y", "y", 1.0), ("U", "u", 1.0), ("I", "i", 1.0), ("O", "o", 1.0), ("P", "p", 1.0), ("@", "@", 1.0), ("[", "[", 1.0), ("Enter", "Key.enter", 1.5)],
		[("Caps", "Key.caps_lock", 1.75), ("A", "a", 1.0), ("S", "s", 1.0), ("D", "d", 1.0), ("F", "f", 1.0), ("G", "g", 1.0), ("H", "h", 1.0), ("J", "j", 1.0), ("K", "k", 1.0), ("L", "l", 1.0), (";", ";", 1.0), (":", ":", 1.0), ("]", "]", 1.0)],
		[("Shift", "Key.shift_l", 2.25), ("Z", "z", 1.0), ("X", "x", 1.0), ("C", "c", 1.0), ("V", "v", 1.0), ("B", "b", 1.0), ("N", "n", 1.0), ("M", "m", 1.0), (",", ",", 1.0), (".", ".", 1.0), ("/", "/", 1.0), ("Shift", "Key.shift_r", 2.75)],
		[("Ctrl", "Key.ctrl_l", 1.25), ("Win", "Key.cmd", 1.25), ("Alt", "Key.alt_l", 1.25), ("Space", "Key.space", 6.25), ("Alt", "Key.alt_r", 1.25), ("Win", "Key.cmd_r", 1.25), ("Menu", "Key.menu", 1.25), ("Ctrl", "Key.ctrl_r", 1.25)],
	],
	[
		[None, None, ("1", "1", 1.0), ("2", "2", 1.0), ("3", "3", 1.0), ("4", "4", 1.0), ("5", "5", 1.0)],
		[("Tab", "Key.tab", 1.5), ("Q", "q", 1.0), ("W", "w", 1.0), ("E", "e", 1.0), ("R", "r", 1.0), ("T", "t", 1.0)],
		[("Caps", "Key.caps_lock", 1.75), ("A", "a", 1.0), ("S", "s", 1.0), ("D", "d", 1.0), ("F", "f", 1.0), ("G", "g", 1.0)],
		[("Shift", "Key.shift_l", 2.25), ("Z", "z", 1.0), ("X", "x", 1.0), ("C", "c", 1.0), ("V", "v", 1.0)],
		[("Ctrl", "Key.ctrl_l", 1.25), ("Win", "Key.cmd", 1.25), ("Alt", "Key.alt_l", 1.25), ("Space", "Key.space", 3)],
	]
]

class Widget(QWidget):
	def __init__(self):
		super().__init__()
		self.keyinput = Keyinput()
		self.mouinput = Mouseinput(int(self.winId()))
		self.trail = deque(maxlen=1000//UPDATE)
		self.virtual_mouse_pos = (WIN[0]-MOUSEPAD[0]//2, WIN[1]-MOUSEPAD[1]//2, 0)
		self.key_size = KEYSIZE
		self.key_spacing = KEYSPACING
		self.setMinimumSize(WIN[0], WIN[1])

		self.bg_color = QColor(0, 255, 0)
		self.key_color = QColor(60, 60, 60)
		self.key_pressed_color = QColor(100, 150, 255)
		self.text_color = QColor(255, 255, 255)
		self.border_color = QColor(80, 80, 80)
	
	def nativeEvent(self, eventType, message):
		msg = ctypes.cast(int(message), ctypes.POINTER(ctypes.wintypes.MSG)).contents
		if msg.message == WM_INPUT:
			self.mouinput.handle_raw_input(msg.lParam)
		return False, 0

	def paintEvent(self, event):
		dx = self.mouinput.dx
		dy = self.mouinput.dy
		self.mouinput.dx = 0
		self.mouinput.dy = 0
		self.virtual_mouse_pos = (self.virtual_mouse_pos[0] + dx, self.virtual_mouse_pos[1] + dy, 'left' in self.mouinput.buttons)
		self.trail.append((self.virtual_mouse_pos[0], self.virtual_mouse_pos[1], self.virtual_mouse_pos[2]))
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.fillRect(self.rect(), self.bg_color)

		y_offset = 20
		
		for row_idx, row in enumerate(key_layouts[MODE=="fps"]):
			x_offset = 20
			for key_data in row:
				if key_data is None:
					x_offset += self.key_size * 0.5 + self.key_spacing
					continue
				
				label, key_code, width_mult = key_data
				key_width = self.key_size * width_mult + self.key_spacing * (width_mult - 1)
				
				is_pressed = self._is_key_pressed(key_code)
				
				self._draw_key(painter, x_offset, y_offset, key_width, self.key_size, label, is_pressed)
				
				x_offset += key_width + self.key_spacing
			
			y_offset += self.key_size + self.key_spacing
		
		painter.setBrush(QBrush(QColor(20, 20, 20)))
		painter.setPen(Qt.NoPen)
		painter.drawRoundedRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1], MOUSEPAD[0], MOUSEPAD[1], 12, 12)
		if 'left' in self.mouinput.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]+50, WIN[1]-MOUSEPAD[1], MOUSEPAD[0]//2-50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'right' in self.mouinput.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2, WIN[1]-MOUSEPAD[1], MOUSEPAD[0]//2-50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'middle' in self.mouinput.buttons:
			painter.setBrush(QBrush(QColor(150, 150, 150)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2-25, WIN[1]-MOUSEPAD[1]+25, 50, WIN[1]-MOUSEPAD[1]//3*2-50)
		if 'x1' in self.mouinput.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1]//2, 50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'x2' in self.mouinput.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1]//6*5, 50, WIN[1]-MOUSEPAD[1]//3*2)
		if self.mouinput.scroll > 0:
			painter.setBrush(QBrush(QColor(100, 100, 100)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2-25, WIN[1]-MOUSEPAD[1]+25, 50, WIN[1]//2-MOUSEPAD[1]//3-25)
		if self.mouinput.scroll < 0:
			painter.setBrush(QBrush(QColor(100, 100, 100)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2-25, WIN[1]//2*3-MOUSEPAD[1]//3*4, 50, WIN[1]//2-MOUSEPAD[1]//3-25)
	
		trail = [((x - self.trail[-1][0])*SENS + WIN[0]-MOUSEPAD[0]//2, (y - self.trail[-1][1])*SENS + WIN[1]-MOUSEPAD[1]//2, z) for x, y, z in self.trail]
		for i in range(len(trail)-1):
			alpha = int(255 * (i / len(trail)))
			if trail[i][2]:
				color = QColor(100, 150, 255, alpha)
			else:
				color = QColor(255, 0, 0, alpha)
			painter.setPen(QPen(color, 3))
			painter.drawLine(trail[i][0], trail[i][1], trail[i+1][0], trail[i+1][1])
		
		self.mouinput.scroll = 0
		
	def _is_key_pressed(self, key_code):
		pressed = self.keyinput.pressed_keys
		
		if key_code in pressed:
			return True
		
		if key_code == "Key.shift_l" or key_code == "Key.shift_r":
			return "Key.shift" in pressed or "Key.shift_l" in pressed or "Key.shift_r" in pressed
		if key_code == "Key.ctrl_l" or key_code == "Key.ctrl_r":
			return "Key.ctrl" in pressed or "Key.ctrl_l" in pressed or "Key.ctrl_r" in pressed
		if key_code == "Key.alt_l" or key_code == "Key.alt_r":
			return "Key.alt" in pressed or "Key.alt_l" in pressed or "Key.alt_r" in pressed
		
		return False

	def _draw_key(self, painter, x, y, width, height, label, is_pressed):
		if is_pressed:
			rect = QRectF(x, y+2, width, height-2)
		else:
			rect = QRectF(x, y, width, height)
		
		if is_pressed:
			painter.setBrush(QBrush(self.key_pressed_color))
		else:
			painter.setBrush(QBrush(self.key_color))
		
		painter.setPen(QPen(self.border_color, 1))
		painter.drawRoundedRect(rect, 5, 5)
		
		painter.setPen(QPen(self.text_color))
		font = QFont("Segoe UI", 9)
		font.setBold(True)
		painter.setFont(font)
		painter.drawText(rect, Qt.AlignCenter, label)

class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PyBoard")
		self.widget = Widget()
		self.setCentralWidget(self.widget)
		self.update_timer = self.startTimer(UPDATE)
	
	def timerEvent(self, event):
		self.widget.update()

MODE = "fps" # full or fps

if MODE == "full":
	UPDATE = 10
	WIN = (1000, 300)
	KEYSIZE = 40
	KEYSPACING = 4
	MOUSEPAD = (300, 300)
	SENS = 0.1
elif MODE == "fps":
	UPDATE = 5
	WIN = (720, 260)
	KEYSIZE = 40
	KEYSPACING = 4
	MOUSEPAD = (400, 260)
	SENS = 0.05

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec())