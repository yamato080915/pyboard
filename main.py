from pynput import keyboard, mouse
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont, QTextOption, QFontMetrics, QIcon
from PySide6.QtCore import Qt, QFileInfo, QDir, QSettings
import sys

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

class Window(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PyBoard")
		self.setGeometry(100, 100, 400, 300)
		self.keyinput = Keyinput()
		self.mouseinput = Mouseinput()
		self.update_timer = self.startTimer(5)

	def timerEvent(self, event):
		keys = self.keyinput.pressed_keys
		pos = self.mouseinput.mouse_pos
		btns = self.mouseinput.mouse_buttons
		scroll = self.mouseinput.mouse_scroll

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec())