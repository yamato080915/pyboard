import ctypes
from ctypes import wintypes
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRectF
import sys
from collections import deque

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
class RAWKEYBOARD(ctypes.Structure):
	_fields_ = [
		("MakeCode", wintypes.USHORT),
		("Flags", wintypes.USHORT),
		("Reserved", wintypes.USHORT),
		("VKey", wintypes.USHORT),
		("Message", wintypes.UINT),
		("ExtraInformation", wintypes.ULONG),
	]
class RAWINPUT_UNION(ctypes.Union):
	_fields_ = [
		("mouse", RAWMOUSE),
		("keyboard", RAWKEYBOARD),
	]
class RAWINPUT(ctypes.Structure):
	_fields_ = [
		("header", RAWINPUTHEADER),
		("data", RAWINPUT_UNION),
	]
class RAWINPUTDEVICE(ctypes.Structure):
	_fields_ = [
		("usUsagePage", wintypes.USHORT),
		("usUsage", wintypes.USHORT),
		("dwFlags", wintypes.DWORD),
		("hwndTarget", wintypes.HWND),
	]
class Input:
	def __init__(self, hwnd=None):
		self.pressed_keys = set()

		rid_key = RAWINPUTDEVICE()
		rid_key.usUsagePage = 0x01
		rid_key.usUsage = 0x06
		rid_key.dwFlags = 0x00000100
		rid_key.hwndTarget = hwnd
		user32.RegisterRawInputDevices(ctypes.byref(rid_key), 1, ctypes.sizeof(rid_key))

		self.dx = 0
		self.dy = 0
		self.buttons = set()
		self.scroll = 0
		rid_mou = RAWINPUTDEVICE()
		rid_mou.usUsagePage = 0x01
		rid_mou.usUsage = 0x02
		rid_mou.dwFlags = 0x00000100
		rid_mou.hwndTarget = hwnd
		user32.RegisterRawInputDevices(ctypes.byref(rid_mou), 1, ctypes.sizeof(rid_mou))

	def handle_raw_keyboard_input(self, raw):
		kb = raw.data.keyboard
		vkey = kb.VKey
		flags = kb.Flags

		if flags & 0x01:
			self.pressed_keys.discard(vkey)
		else:
			self.pressed_keys.add(vkey)

	def handle_raw_mouse_input(self, lParam):
		size = wintypes.UINT(0)
		user32.GetRawInputData(lParam, RID_INPUT, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
		buffer = ctypes.create_string_buffer(size.value)
		user32.GetRawInputData(lParam, RID_INPUT, buffer, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
		raw = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents
		if raw.header.dwType == 0:
			mouse = raw.data.mouse
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

key_nums = {
	"Esc": 27, "F1": 112, "F2": 113, "F3": 114, "F4": 115, "F5": 116, "F6": 117, "F7": 118, "F8": 119, "F9": 120, "F10": 121, "F11": 122, "F12": 123,
	"1": 49, "2": 50, "3": 51, "4": 52, "5": 53, "6": 54, "7": 55, "8": 56, "9": 57, "0": 48, "-": 189, "^": 222, "\\": 220, "BS": 8,
	"Tab": 9, "Q": 81, "W": 87, "E": 69, "R": 82, "T": 84, "Y": 89, "U": 85, "I": 73, "O": 79, "P": 80, "@": 192, "[": 219, "Enter": 13, 
	"Caps": 240, "A": 65, "S": 83, "D": 68, "F": 70, "G": 71, "H": 72, "J": 74, "K": 75, "L": 76, ";": 187, ":": 186, "]": 221,
	"Shift": 16, "Z": 90, "X": 88, "C": 67, "V": 86, "B": 66, "N": 78, "M": 77, ",": 188, ".": 190, "/": 191,
	"Ctrl": 17, "Win": 91, "Alt": 18, "Space": 32, "Menu": 93,
}

key_layouts = [
	[
		[("Esc", 1.0), 0.5, ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0), 0.5, ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), 0.5, ("F9", 1.0), ("F10", 1.0), ("F11", 1.0), ("F12", 1.0)],
		[1.0, ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0), ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0), ("0", 1.0), ("-", 1.0), ("^", 1.0), ("\\", 1.0), ("BS", 1.0)],
		[("Tab", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0), ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0), ("P", 1.0), ("@", 1.0), ("[", 1.0), ("Enter", 1.5)],
		[1.75, ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0), ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0), (";", 1.0), (":", 1.0), ("]", 1.0)],
		[("Shift", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0), ("B", 1.0), ("N", 1.0), ("M", 1.0), (",", 1.0), (".", 1.0), ("/", 1.0), ("Shift", 2.75)],
		[("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("Space", 6.25), ("Alt", 1.25), ("Win", 1.25), ("Menu", 1.25), ("Ctrl", 1.25)],
	],
	[
		[1.0, ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0), ("5", 1.0)],
		[("Tab", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0), ("T", 1.0)],
		[1.75, ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0), ("G", 1.0)],
		[("Shift", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0)],
		[("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("Space", 3)],
	]
]

class Widget(QWidget):
	def __init__(self):
		super().__init__()
		self.input = Input(int(self.winId()))
		self.trail = deque(maxlen=1000//UPDATE)
		self.virtual_mouse_pos = (WIN[0]-MOUSEPAD[0]//2, WIN[1]-MOUSEPAD[1]//2, 0)
		self.key_size = KEYSIZE
		self.key_spacing = KEYSPACING
		self.scroll_count = 0
		self.setMinimumSize(WIN[0], WIN[1])

		self.bg_color = QColor(0, 255, 0)
		self.key_color = QColor(60, 60, 60)
		self.key_pressed_color = QColor(100, 150, 255)
		self.text_color = QColor(255, 255, 255)
		self.border_color = QColor(80, 80, 80)
	
	def nativeEvent(self, eventType, message):
		msg = ctypes.cast(int(message), ctypes.POINTER(ctypes.wintypes.MSG)).contents
		if msg.message == WM_INPUT:
			size = wintypes.UINT(0)
			user32.GetRawInputData(msg.lParam, RID_INPUT, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))

			buffer = ctypes.create_string_buffer(size.value)
			user32.GetRawInputData(msg.lParam, RID_INPUT, buffer, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))

			raw = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents

			if raw.header.dwType == 0:
				self.input.handle_raw_mouse_input(msg.lParam)
			elif raw.header.dwType == 1:
				self.input.handle_raw_keyboard_input(raw)
			
		return False, 0

	def paintEvent(self, event):
		dx = self.input.dx
		dy = self.input.dy
		self.input.dx = 0
		self.input.dy = 0
		self.virtual_mouse_pos = (self.virtual_mouse_pos[0] + dx, self.virtual_mouse_pos[1] + dy, 'left' in self.input.buttons)
		self.trail.append((self.virtual_mouse_pos[0], self.virtual_mouse_pos[1], self.virtual_mouse_pos[2]))
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.fillRect(self.rect(), self.bg_color)

		y_offset = 20
		
		for row in key_layouts[MODE=="fps"]:
			x_offset = 20
			for key_data in row:
				if type(key_data) is float:
					x_offset += self.key_size*key_data + self.key_spacing
					continue
				
				label, width_mult = key_data
				key_width = self.key_size * width_mult + self.key_spacing * (width_mult - 1)
				
				is_pressed = self._is_key_pressed(key_nums[label])
				
				self._draw_key(painter, x_offset, y_offset, key_width, self.key_size, label, is_pressed)
				
				x_offset += key_width + self.key_spacing
			
			y_offset += self.key_size + self.key_spacing
		
		painter.setBrush(QBrush(QColor(20, 20, 20)))
		painter.setPen(Qt.NoPen)
		painter.drawRoundedRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1], MOUSEPAD[0], MOUSEPAD[1], 12, 12)
		if 'left' in self.input.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]+50, WIN[1]-MOUSEPAD[1], MOUSEPAD[0]//2-50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'right' in self.input.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2, WIN[1]-MOUSEPAD[1], MOUSEPAD[0]//2-50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'middle' in self.input.buttons:
			painter.setBrush(QBrush(QColor(150, 150, 150)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2-25, WIN[1]-MOUSEPAD[1]+25, 50, WIN[1]-MOUSEPAD[1]//3*2-50)
		if 'x1' in self.input.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1]//2, 50, WIN[1]-MOUSEPAD[1]//3*2)
		if 'x2' in self.input.buttons:
			painter.setBrush(QBrush(QColor(200, 200, 200)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0], WIN[1]-MOUSEPAD[1]//6*5, 50, WIN[1]-MOUSEPAD[1]//3*2)
		if self.input.scroll > 0:
			painter.setBrush(QBrush(QColor(100, 100, 100)))
			painter.setPen(Qt.NoPen)
			painter.drawRect(WIN[0]-MOUSEPAD[0]//2-25, WIN[1]-MOUSEPAD[1]+25, 50, WIN[1]//2-MOUSEPAD[1]//3-25)
		if self.input.scroll < 0:
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
		
		self.scroll_count += 1
		if self.scroll_count == 125//UPDATE:
			self.input.scroll = 0
			self.scroll_count = 0

	def _is_key_pressed(self, key_code):
		pressed = self.input.pressed_keys
		
		if key_code in pressed:
			return True
		
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