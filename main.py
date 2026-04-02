from pynput import keyboard, mouse
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

class Mouseinput:
	def __init__(self):
		self.mouse_pos = (0, 0)
		self.mouse_buttons = set()
		self.mouse_scroll = 0
		self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
		self.listener.start()
	
	def on_move(self, x, y):
		self.mouse_pos = (x, y)
	
	def on_click(self, x, y, button, pressed):
		if pressed:
			self.mouse_buttons.add(button)
		else:
			self.mouse_buttons.discard(button)

	def on_scroll(self, x, y, dx, dy):
		self.mouse_scroll += dy

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
		self.mouseinput = Mouseinput()
		self.trail = deque(maxlen=60)
		self.key_size = 40
		self.key_spacing = 4
		self.setMinimumSize(600, 260)

		self.bg_color = QColor(0, 255, 0)
		self.key_color = QColor(60, 60, 60)
		self.key_pressed_color = QColor(100, 150, 255)
		self.text_color = QColor(255, 255, 255)
		self.border_color = QColor(80, 80, 80)
	
	def paintEvent(self, event):
		self.trail.append(self.mouseinput.mouse_pos)
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)
		painter.fillRect(self.rect(), self.bg_color)

		y_offset = 20
		
		for row_idx, row in enumerate(key_layouts[1]):
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
		painter.drawRoundedRect(320, 0, 280, 260, 12, 12)

		sens = 0.2
		trail = [((x - self.trail[-1][0])*sens + 460, (y - self.trail[-1][1])*sens + 130) for x, y in self.trail]
		for i in range(len(trail)-1):
			alpha = int(255 * (i / len(trail)))
			color = QColor(255, 0, 0, alpha)
			painter.setPen(QPen(color, 3))
			painter.drawLine(trail[i][0], trail[i][1], trail[i+1][0], trail[i+1][1])
		
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
		self.update_timer = self.startTimer(16)
	
	def timerEvent(self, event):
		self.widget.update()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec())