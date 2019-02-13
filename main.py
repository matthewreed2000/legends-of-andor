from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.image import Image

import time

Builder.load_string('''
<Platform>:
	text: "platform"
	canvas:
		Color:
			rgba: self.colorList
		Rectangle:
			pos:self.pos
			size:self.size

<Wall>:
	text: "wall"
	canvas:
		Color:
			rgba: self.colorList
		Rectangle:
			pos:self.pos
			size:self.size

<EmptyBlock>:
	text: "empty"
	canvas:
		Color:
			rgba: self.colorList
		Rectangle:
			pos:self.pos
			size:self.size

<Enemy>:
	text: "enemy"
	canvas:
		Color:
			rgba: self.colorList
		Rectangle:
			pos:self.pos
			size:self.size

<LoAGame>:
	size_hint: 1, 1
	canvas:
		Color:
			rgba: self.colorList
		Rectangle:
			pos:self.pos
			size:self.size

	player: player1

	PlayerSprite:
		id: player1
		text: "Player"
		canvas:
			Color:
				rgba: self.colorList
			Rectangle:
				pos: self.pos
				size: self.size
''')
class PlayerSprite(Widget):
	colorList = ListProperty([0, 1, 0, 1])
	blockHeightNorm = NumericProperty(3)
	blockHeightCrouch = NumericProperty(1.5)
	crouchTime = NumericProperty(0)
	blockWidth = NumericProperty(2)
	blockHeight = NumericProperty(3)
	blockArea = ReferenceListProperty(blockWidth, blockHeight)
	blockPos_x = NumericProperty(20)
	blockPos_y = NumericProperty(4)
	blockPos = ReferenceListProperty(blockPos_x, blockPos_y)

	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)
	onGround = NumericProperty(1)
	groundHeight = NumericProperty(0)
	frictionFactor = NumericProperty(0.5)
	slipFactor = NumericProperty(0.5)
	hSpeed = NumericProperty(0.3)
	vSpeed = NumericProperty(0.55)
	health = NumericProperty(10)
	maxHealth = NumericProperty(10)
	invincibility = NumericProperty(60)
	lives = NumericProperty(3)

	keys = [0]
	for i in range(6):
		keys.append(0)

	def resize(self, blockSize):
		self.size = blockSize * Vector(self.blockArea)
		self.pos = blockSize * Vector(self.blockPos)
	def repos(self, blockSize):
		self.pos = blockSize * Vector(self.blockPos)
	def respawn(self):
		self.health = self.maxHealth
		self.invincibility = 60

		self.crouchTime = 0
		self.blockPos = self.parent.spawnBlock.blockPos
		self.groundHeight = self.parent.spawnBlock.blockPos_y
		self.velocity = [0, 0]

		self.parent.loadBlockMin.blockPos_x = self.parent.startBlock.blockPos_x + 1
		self.parent.loadBlockMin.blockPos_y = self.parent.startBlock.blockPos_y
		self.parent.loadBlockMax.blockPos_x = self.parent.startBlock.blockPos_x - 1
		self.parent.loadBlockMax.blockPos_y = self.parent.startBlock.blockPos_y
	def kill(self):
		self.lives -= 1
		if self.lives >= 0:
			self.respawn()

class Enemy(Widget):
	colorList = ListProperty([0.2, 0, 0, 1])
	blockHeightNorm = NumericProperty(3)
	blockHeightCrouch = NumericProperty(1.5)
	crouchTime = NumericProperty(0)
	blockWidth = NumericProperty(2)
	blockHeight = NumericProperty(3)
	blockArea = ReferenceListProperty(blockWidth, blockHeight)
	blockPos_x = NumericProperty(4)
	blockPos_y = NumericProperty(4)
	blockPos = ReferenceListProperty(blockPos_x, blockPos_y)

	velocity_x = NumericProperty(0)
	velocity_y = NumericProperty(0)
	velocity = ReferenceListProperty(velocity_x, velocity_y)
	onGround = NumericProperty(1)
	groundHeight = NumericProperty(0)
	frictionFactor = NumericProperty(0.5)
	slipFactor = NumericProperty(0.5)
	hSpeed = NumericProperty(0.15)
	vSpeed = NumericProperty(0.55)
	health = NumericProperty(10)
	invincibility = NumericProperty(0)

	keys = [0 for i in range(7)]

	def setup(self, pos_x, pos_y):
		self.blockPos_x = pos_x
		self.blockPos_y = pos_y
	def resize(self, blockSize):
		self.size = blockSize * Vector(self.blockArea)
		self.pos = blockSize * Vector(self.blockPos)
	def repos(self, blockSize):
		self.pos = blockSize * Vector(self.blockPos)
	def spawn(self, spawnBlock):
			self.blockPos = spawnBlock.blockPos
			self.groundHeight = spawnBlock.blockPos_y
			self.velocity = [0, 0]
	def remove(self):
		self.parent.remove_widget(self)
	def kill(self):
		self.remove()

class EmptyBlock(Widget):
	colorList = ListProperty([0, 0, 0, 0.2])
	blockWidth = NumericProperty(1)
	blockHeight = NumericProperty(1)
	blockArea = ReferenceListProperty(blockWidth, blockHeight)
	blockPos_x = NumericProperty(0)
	blockPos_y = NumericProperty(0)
	blockPos = ReferenceListProperty(blockPos_x, blockPos_y)
	def setup(self, pos_x, pos_y):
		self.blockPos_x = pos_x
		self.blockPos_y = pos_y
	def resize(self, blockSize):
		self.size = blockSize * Vector(self.blockArea)
		self.pos = blockSize * Vector(self.blockPos)
	def repos(self, blockSize):
		self.pos = blockSize * Vector(self.blockPos)
	def remove(self):
		self.parent.remove_widget(self)

class Platform(Widget):
	colorList = ListProperty([1, 1, 1, 1])
	blockWidth = NumericProperty(1)
	blockHeight = NumericProperty(1)
	blockArea = ReferenceListProperty(blockWidth, blockHeight)
	blockPos_x = NumericProperty(0)
	blockPos_y = NumericProperty(0)
	blockPos = ReferenceListProperty(blockPos_x, blockPos_y)
	def setup(self, size_x, size_y, pos_x, pos_y):
		self.blockWidth = size_x
		self.blockHeight = size_y
		self.blockPos_x = pos_x
		self.blockPos_y = pos_y
	def resize(self, blockSize):
		self.size = blockSize * Vector(self.blockArea)
		self.pos = blockSize * Vector(self.blockPos)
	def repos(self, blockSize):
		self.pos = blockSize * Vector(self.blockPos)
	def testCollide(self, testObject, blockSize, dy):
		w1 = self.blockWidth
		h1 = 1.0 / blockSize
		x1 = self.blockPos_x
		y1 = self.blockPos_y + self.blockHeight - h1
		w2 = testObject.blockWidth
		h2 = abs(dy)
		x2 = testObject.blockPos_x
		y2 = testObject.blockPos_y + dy
		self.tempWid1 = Widget(size=(w1, h1), pos=(x1, y1))
		self.tempWid2 = Widget(size=(w2, h2), pos=(x2, y2))
		if self.tempWid1.collide_widget(self.tempWid2) and testObject.crouchTime < 20:
			testObject.onGround = 1
			testObject.groundHeight = self.blockPos_y + self.blockHeight
		self.remove_widget(self.tempWid1)
		self.remove_widget(self.tempWid2)
	def remove(self):
		self.parent.remove_widget(self)

class Wall(Widget):
	colorList = ListProperty([1, 1, 0, 1])
	blockWidth = NumericProperty(1)
	blockHeight = NumericProperty(1)
	blockArea = ReferenceListProperty(blockWidth, blockHeight)
	blockPos_x = NumericProperty(0)
	blockPos_y = NumericProperty(0)
	blockPos = ReferenceListProperty(blockPos_x, blockPos_y)
	def setup(self, size_x, size_y, pos_x, pos_y):
		self.blockWidth = size_x
		self.blockHeight = size_y
		self.blockPos_x = pos_x
		self.blockPos_y = pos_y
	def resize(self, blockSize):
		self.size = blockSize * Vector(self.blockArea)
		self.pos = blockSize * Vector(self.blockPos)
	def repos(self, blockSize):
		self.pos = blockSize * Vector(self.blockPos)
	def testCollide(self, testObject, blockSize, dy, dx):
		self.tempWid = Widget(size=(self.blockWidth, self.blockHeight), pos=(self.blockPos_x, self.blockPos_y))
		if dy > 0:
			w1 = testObject.blockWidth - 2.0 / blockSize
			h1 = dy
			x1 = testObject.blockPos_x + 1.0 / blockSize
			y1 = testObject.blockPos_y + testObject.blockHeight
		if dy <= 0:
			w1 = testObject.blockWidth - 2.0 / blockSize
			h1 = abs(dy)
			x1 = testObject.blockPos_x + 1.0 / blockSize
			y1 = testObject.blockPos_y + dy
		self.tempWid1 = Widget(size=(w1, h1), pos=(x1, y1))
		if self.tempWid.collide_widget(self.tempWid1):
			if dy > 0:
				testObject.velocity_y = 0
				testObject.blockPos_y = self.blockPos_y - testObject.blockHeight
			elif dy <= 0:
				testObject.onGround = 1
				testObject.groundHeight = self.blockPos_y + self.blockHeight
				testObject.blockPos_y = testObject.groundHeight

		if dx > 0:
			w2 = dx
			h2 = testObject.blockHeight - 2.0 / blockSize
			x2 = testObject.blockPos_x + testObject.blockWidth
			y2 = testObject.blockPos_y + 1.0 / blockSize
		if dx <= 0:
			w2 = abs(dx)
			h2 = testObject.blockHeight - 2.0 / blockSize
			x2 = testObject.blockPos_x + dx
			y2 = testObject.blockPos_y + 1.0 / blockSize
		self.tempWid2 = Widget(size=(w2, h2), pos=(x2, y2))
		if self.tempWid.collide_widget(self.tempWid2):
			if dx > 0:
				testObject.velocity_x = 0
				testObject.blockPos_x = self.blockPos_x - testObject.blockWidth
			elif dx <= 0:
				testObject.velocity_x = 0
				testObject.blockPos_x = self.blockPos_x + self.blockWidth
		if self.text == "kill" and (self.tempWid.collide_widget(self.tempWid1) or self.tempWid.collide_widget(self.tempWid2)):
			try:
				testObject.kill()
			except Exception as e:
				print(e)
		self.remove_widget(self.tempWid1)
		self.remove_widget(self.tempWid2)
		self.remove_widget(self.tempWid)
	def remove(self):
		self.parent.remove_widget(self)

class LoAGame(Widget):
	colorList = ListProperty([0, 0.5, 1, 1])
	importantList = ["Player", "loadBlock", "startBlock", "endBlock", "spawnBlock", "enemy"]
	blockSize = NumericProperty(1)
	cameraSpeed_x = NumericProperty(0)
	cameraSpeed_y = NumericProperty(0)
	gravity = NumericProperty(0.03)

	player = ObjectProperty(None)
	loadBlockMin = ObjectProperty(None)
	loadBlockMax = ObjectProperty(None)
	startBlock = ObjectProperty(None)
	endBlock = ObjectProperty(None)
	spawnBlock = ObjectProperty(None)

	levelNum = 1
	levelNumMax = 1
	levelImage = Image("Level_" + str(levelNum) + ".png").texture
	topRowPixels = levelImage.get_region(0, levelImage.height, levelImage.width, 1)
	topRowList = [int(ord(pix)/ 25.6) for pix in topRowPixels.pixels]
	topRow = [topRowList[i:i+4] for i in range(0, len(topRowList), 4)]

	test = [(6, 8), (16, 8), (16, 3), (30, 3), (16, 3), (16, 8), (25, 8), (25, 13), (25, 8)]
	enemy = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(LoAGame, self).__init__(**kwargs)
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)
		self._keyboard.bind(on_key_up=self._on_keyboard_up)

		self.empty = EmptyBlock()
		self.add_widget(self.empty)

		self.posBlock = EmptyBlock(text="placeholder", colorList=[0, 0, 0, 1])
		self.posBlock.setup(0, 0)
		self.add_widget(self.posBlock)

		self.enemy = Enemy()
		self.enemy.setup(19, 7)
		self.add_widget(self.enemy)

		self.startBlock = EmptyBlock(text="startBlock", colorList=[0, 0, 0, 0.2])
		self.startBlock.setup(0, 0)
		self.add_widget(self.startBlock)

		self.endBlock = EmptyBlock(text="endBlock", colorList=[0, 1, 1, 1])
		self.endBlock.setup(0, 0)
		self.add_widget(self.endBlock)

		self.spawnBlock = EmptyBlock(text="spawnBlock", colorList=[0, 0, 0, 0.2])
		self.spawnBlock.setup(19, 7)
		self.add_widget(self.spawnBlock)

		self.loadBlockMin = EmptyBlock(text="loadBlock", colorList=[1, 1, 1, 0.2])
		self.loadBlockMin.setup(0, 0)
		self.add_widget(self.loadBlockMin)
		self.loadBlockMax = EmptyBlock(text="loadBlock", colorList=[1, 1, 1, 0.2])
		self.loadBlockMax.setup(0, 0)
		self.add_widget(self.loadBlockMax)

		self.newLevel(1)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard.unbind(on_key_up=self._on_keyboard_up)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		if keycode[1] == 'w':
			self.player.keys[0] = 1
		if keycode[1] == 'a':
			self.player.keys[1] = 1
		if keycode[1] == 's':
			self.player.keys[2] = 1
		if keycode[1] == 'd':
			self.player.keys[3] = 1
		if keycode[1] == 'r':
			self.player.keys[4] = 1
		if keycode[1] == 'q':
			self.player.keys[5] = 1
	def _on_keyboard_up(self, keyboard, keycode):
		if keycode[1] == 'w':
			self.player.keys[0] = 0
		if keycode[1] == 'a':
			self.player.keys[1] = 0
		if keycode[1] == 's':
			self.player.keys[2] = 0
		if keycode[1] == 'd':
			self.player.keys[3] = 0
		if keycode[1] == 'r':
			self.player.keys[4] = 0
		if keycode[1] == 'q':
			self.player.keys[5] = 0
	def layout(self, *args):
		if self.width * self.height != 0:
			self.cameraSpeed_x = self.width / 50.
			self.cameraSpeed_y = self.height / 50.

			if self.width < self.height:
				self.blockSize = self.width / 20.
			else:
				self.blockSize = self.height / 20.
		for child in self.children:
			child.resize(self.blockSize)
	def on_pos(self, *args):
		Clock.schedule_once(self.layout, -1)
	def on_size(self, *args):
		Clock.schedule_once(self.layout, -1)

	def pixelTest(self, dim, texture, axis):
		if axis == 1:
			pixel = texture.get_region(dim, 0, 1, texture.height)
		if axis == 2:
			pixel = texture.get_region(0, dim, texture.width, 1)
		dataList = [int(ord(pix) / 25.6) for pix in pixel.pixels]
		return [dataList[i:i+4] for i in range(0, len(dataList), 4)]
	def newLevel(self, level):
		self.levelNum = level
		self.levelImage = Image("Level_" + str(self.levelNum) + ".png").texture
		self.topRowPixels = self.levelImage.get_region(0, self.levelImage.height, self.levelImage.width, 1)
		self.topRowList = [int(ord(pix)/ 25.6) for pix in self.topRowPixels.pixels]
		self.topRow = [self.topRowList[i:i+4] for i in range(0, len(self.topRowList), 4)]
		self.spawnBlock.blockPos = self.startBlock.blockPos
		self.endBlock.blockPos = self.startBlock.blockPos
		self.loadBlockMin.blockPos = self.startBlock.blockPos
		self.loadBlockMax.blockPos = self.startBlock.blockPos
		while self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x < int(self.levelImage.width / 2) - 2:
			self.loadBlockMax.blockPos_x += 1
			self.loadLevelArea(int((self.loadBlockMin.blockPos_x - self.startBlock.blockPos_x)), int((self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x)), self.levelImage)
		self.moveLoadBlocks()
		self.player.respawn()
		self.bgCenter(1, 1)
	def loadLevelArea(self, xMin, xMax, texture):
		y = 0
		xMax *= 2
		debugTime = time.time()
		if self.topRow[xMax] == [9, 0, 0, 9] or self.topRow[xMax] == [9, 0, 9, 9]:
			pixelsY = self.pixelTest(xMax, texture, 1)
			for y in range(1, len(pixelsY)):
				if pixelsY[y] == [9, 0, 0, 9] or pixelsY[y] == [9, 0, 9, 9]:
					pixelsX = self.pixelTest(texture.height - y - 2, texture, 2)
					if pixelsX[xMax + 1] == [9, 0, 0, 9] or pixelsX[xMax + 1] == [9, 0, 9, 9]:
						dx = 0
						w = 1
						h = 1
						widType = pixelsY[y + 1]
						while xMax + dx + 1 < texture.width and pixelsX[xMax + dx + 1] != [0, 0, 9, 9] and pixelsX[xMax + dx + 1] != [9, 0, 9, 9]:
							dx += 2
							w += 1
						while y < texture.height and pixelsY[y] != [0, 0, 9, 9] and pixelsY[y] != [9, 0, 9, 9]:
							y += 2
							h += 1
						xPos = xMax / 2
						yPos = (texture.height - y) / 2
						#print(w, h, xPos, yPos, widType)
						self.createWidget(w, h, xPos, yPos, widType)

		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "xMax")
		xMin *= 2
		debugTime = time.time()
		if self.topRow[xMin] == [0, 0, 9, 9] or self.topRow[xMin] == [9, 0, 9, 9]:
			pixelsY = self.pixelTest(xMin, texture, 1)
			for y in range(1, len(pixelsY)):
				if pixelsY[y] == [9, 0, 0, 9] or pixelsY[y] == [9, 0, 9, 9]:
					pixelsX = self.pixelTest(texture.height - y - 2, texture, 2)
					if pixelsX[xMin + 1] == [0, 0, 9, 9] or pixelsX[xMin + 1] == [9, 0, 9, 9]:
						dx = 0
						w = 1
						h = 1
						widType = pixelsY[y + 1]
						while xMin - dx + 1 >= 0 and pixelsX[xMin - dx + 1] != [9, 0, 0, 9] and pixelsX[xMin - dx + 1] != [9, 0, 9, 9]:
							dx += 2
							w += 1
						while y < texture.height and pixelsY[y] != [0, 0, 9, 9] and pixelsY[y] != [9, 0, 9, 9]:
							y += 2
							h += 1
						xPos = xMin / 2 - w + 1
						yPos = (texture.height - y) / 2
						self.createWidget(w, h, xPos, yPos, widType)
		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "xMin")
	def unloadLevelArea(self):
		for child in self.children:
			if child.text not in self.importantList:
				if child.blockPos_x > self.loadBlockMax.blockPos_x + 1:
					#print("Removing", child)
					child.remove()
				elif child.blockPos_x + child.blockWidth < self.loadBlockMin.blockPos_x - 2:
					#print("Removing", child)
					child.remove()
	def createWidget(self, w, h, levX, levY, widType):
		x = levX + self.startBlock.blockPos_x
		y = levY + self.startBlock.blockPos_y
		collided = 0
		for child in self.children:
			if child.collide_point((x + 0.5) * self.blockSize, (y + 0.5) * self.blockSize) and child.text not in self.importantList:
				#print("Collided", levX, levY, child.text, widType)
				collided = 1
		if collided == 0:
			if widType == [9, 9, 0, 9]:
				wall = Wall()
				wall.setup(w, h, x, y)
				wall.resize(self.blockSize)
				self.add_widget(wall)
			elif widType == [9, 9, 9, 9]:
				platform = Platform()
				platform.setup(w, h, x, y)
				platform.resize(self.blockSize)
				self.add_widget(platform)
			elif widType == [5, 0, 0, 9]:
				wall = Wall(text="kill", colorList=[0.5, 0, 0, 1])
				wall.setup(w, h, x, y)
				wall.resize(self.blockSize)
				self.add_widget(wall)
			elif widType == [0, 5, 0, 9]:
				self.spawnBlock.blockPos = (x, y)
			elif widType == [0, 9, 9, 9]:
				self.endBlock.blockPos = (x, y)
			else:
				wall = Wall(text="placeholder", colorList=[0, 0, 0, 1])
				wall.setup(w, h, x, y)
				wall.resize(self.blockSize)
				self.add_widget(wall)
	def goto(self, wid, point):
		wid.keys = [0 for i in wid.keys]
		if wid.blockPos_x - self.startBlock.blockPos_x + wid.blockWidth < point[0]:
			wid.keys[3] = 1
		if wid.blockPos_x - self.startBlock.blockPos_x > point[0]:
			wid.keys[1] = 1
		if wid.blockPos_y - self.startBlock.blockPos_y + wid.blockHeight < point[1]:
			wid.keys[0] = 1
		if wid.blockPos_y - self.startBlock.blockPos_y > point[1]:
			wid.keys[2] = 1
	def moveWid(self, wid):
		wid.velocity_x *= wid.slipFactor
		wid.velocity_y -= self.gravity

		if wid.keys[0] == 1 and wid.onGround > 0 and wid.velocity_y >= -self.gravity and wid.velocity_y <= 0.1 and wid.blockHeight != wid.blockHeightCrouch:
			wid.velocity_y = wid.vSpeed
		if wid.keys[2] == 1 and wid.onGround == 0:
			wid.velocity_y -= wid.vSpeed / 5
		if wid.keys[2] == 1 and wid.onGround == 1:
			wid.crouchTime += 1
			wid.blockHeight = wid.blockHeightCrouch
			wid.resize(self.blockSize)
		elif wid.keys[2] == 0:
			list1 = [(child.text != "platform") * (child.collide_widget(wid)) for child in self.children]
			wid.crouchTime = 0
			wid.blockHeight = wid.blockHeightNorm
			wid.resize(self.blockSize)
			list2 = [(child.text != "platform") * (child.collide_widget(wid)) for child in self.children]
			if list2 != list1:
				wid.blockHeight = wid.blockHeightCrouch
				wid.resize(self.blockSize)

		if wid.blockPos_y + wid.velocity_y - self.startBlock.blockPos_y < -1:
			wid.kill()
		if wid.keys[1] == 1 and wid.velocity_x > - wid.hSpeed:
			wid.velocity_x = wid.velocity_x - (wid.hSpeed * wid.frictionFactor)
		if wid.keys[3] == 1 and wid.velocity_x < wid.hSpeed:
			wid.velocity_x = wid.velocity_x + (wid.hSpeed * wid.frictionFactor)
		if wid.blockPos_x + wid.velocity_x - self.startBlock.blockPos_x < 0:
			wid.velocity_x = 0
			wid.blockPos_x = self.startBlock.blockPos_x
		if wid.blockPos_x + wid.velocity_x + wid.blockWidth - self.startBlock.blockPos_x > self.levelImage.width / 2 - 2:
			wid.velocity_x = 0
			wid.blockPos_x = self.startBlock.blockPos_x + self.levelImage.width / 2 - 2 - wid.blockWidth
		wid.onGround = 0

		for child in self.children:
			try:
				if child.text == "platform":
					child.testCollide(wid, self.blockSize, wid.velocity_y)
				elif child.text == "wall" or child.text == "kill":
					child.testCollide(wid, self.blockSize, wid.velocity_y, wid.velocity_x)
			except Exception as e:
				print(e)
		newPos = Vector(wid.blockPos) + Vector(wid.velocity)
		if wid.onGround > 0:
			if wid.velocity_y <= 0:
				wid.velocity_y = 0
				newPos[1] = wid.groundHeight
		if wid.onGround == 1:
			wid.frictionFactor = 0.5
			wid.slipFactor = 0.5
		else:
			wid.frictionFactor = 0.1
			wid.slipFactor = 1
		wid.blockPos = newPos
		wid.repos(self.blockSize)

	def bgMove(self, x, y):
		for child in self.children:
			child.blockPos = Vector(child.blockPos) + [x, y]
			child.repos(self.blockSize)

	def bgCenter(self, camX, camY):
		x_dist = ((self.width - self.player.width) / 2 - self.player.pos[0]) / self.blockSize
		y_dist = ((self.height - self.player.height) / 3 - self.player.pos[1]) / self.blockSize
		x_mov = x_dist / camX
		y_mov = y_dist / camY
		self.bgMove(x_mov, y_mov)

	def moveLoadBlocks(self):
		while self.loadBlockMax.blockPos_x * self.blockSize - self.width < 1 * self.blockSize and self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x < int(self.levelImage.width / 2) - 2:
			self.loadBlockMax.blockPos_x += 1
			self.loadLevelArea(int((self.loadBlockMin.blockPos_x - self.startBlock.blockPos_x)), int((self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x)), self.levelImage)
		while self.loadBlockMax.blockPos_x * self.blockSize - self.width > 2 * self.blockSize and self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x > 1:
			self.loadBlockMax.blockPos_x -= 1
			self.unloadLevelArea()
		while self.loadBlockMin.blockPos_x > -2 and self.loadBlockMin.blockPos_x - self.startBlock.blockPos_x > 1:
			self.loadBlockMin.blockPos_x -= 1
			self.loadLevelArea(int((self.loadBlockMin.blockPos_x - self.startBlock.blockPos_x)), int((self.loadBlockMax.blockPos_x - self.startBlock.blockPos_x)), self.levelImage)
		while self.loadBlockMin.blockPos_x < -1 and self.loadBlockMin.blockPos_x - self.startBlock.blockPos_x < int(self.levelImage.width / 2) - 2:
			self.loadBlockMin.blockPos_x += 1
			self.unloadLevelArea()

	def update(self, dt):

		#Load Blocks
		debugTime = time.time()
		self.moveLoadBlocks()
		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "Load Block")
		#AI Control

		#Reset
		if self.player.keys[4] == 1:
			self.player.respawn()
		#Player Control
		debugTime = time.time()
		self.posBlock.blockPos_x = self.test[0][0] + self.startBlock.blockPos_x
		self.posBlock.blockPos_y = self.test[0][1] + self.startBlock.blockPos_y
		if self.enemy.collide_point((self.test[0][0] + self.startBlock.blockPos_x)* self.blockSize, (self.test[0][1] + self.startBlock.blockPos_y)* self.blockSize):
			self.test = [self.test[i-1] for i in range(0, len(self.test))]
		self.goto(self.enemy, self.test[0])
		self.moveWid(self.enemy)
		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "Move Enemy")

		debugTime = time.time()
		self.moveWid(self.player)
		#print(self.player.lives, self.player.health, self.player.invincibility)
		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "Move Player")

		if self.player.collide_widget(self.endBlock) and self.levelNum < self.levelNumMax:
			self.newLevel(self.levelNum+1)
		if self.player.collide_widget(self.enemy) and self.player.invincibility <= 0:
			self.player.health -= 1
			self.player.invincibility = 60
		if self.player.invincibility > 0:
			self.player.invincibility -= 1
		if self.player.health <= 0:
			self.player.kill()
		#print(self.player.lives, self.player.health, self.player.invincibility)

		if self.player.keys[5] == 1:
			self.bgCenter(1, 1)
			Clock.unschedule(self.update)
			Clock.schedule_interval(self.update, 1.0 / 2.0)
		if self.player.keys[5] == 0:
			Clock.unschedule(self.update)
			Clock.schedule_interval(self.update, 1.0/ 60.0)
		debugTime = time.time()
		self.bgCenter(self.cameraSpeed_x, self.cameraSpeed_y)
		if time.time() - debugTime > 0.01:
			print(time.time() - debugTime, "bgCenter")

class LoAApp(App):
	def build(self):
		game = LoAGame()
		game.layout()
		Clock.schedule_interval(game.update, 1.0/60.0) #0.6)
		return game

if __name__ == "__main__":
	LoAApp().run()
