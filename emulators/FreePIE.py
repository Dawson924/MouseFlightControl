import ctypes

class vjoyAxis():
	def __init__(self, x, y, z, th_l, th_r):
		self.x, self.y, self.z = x, y, z
		self.th_l, self.th_r = th_l, th_r

class vjoyState():
	def __init__(self, stick, throttle, mouselock, vjoy_botton):
		self.stick = stick
		self.th = throttle
		self.mouselock = mouselock
		self.btn = vjoy_botton

class vjoySensitive():
	def __init__(self, mou, x, y, th):
		self.mou = mou
		self.x, self.y = x, y
		self.th = th


def toggle_enabled(enabled):
	State.stick = enabled
	State.th = enabled
	State.mouselock = enabled
	State.btn = enabled

def reset_axis_pos():
	if Axis.x != center_axis_y :
		Axis.x = 0
	if Axis.y != center_axis_y :
		Axis.y = 0

def check_overflow(a, min, max):
	if a < min:
		a = min
	elif a > max:
		a = max

def wheel_th(sens_mo, sens_th):
	res = 0
	if mouse.wheelUp:
		res += 20*sens_mo*sens_th
	if mouse.wheelDown:
		res -= 20*sens_mo*sens_th

	return res


if starting:
	enabled = False

	# set max and min value
	axis_max = vJoy[0].axisMax
	axis_min = -vJoy[0].axisMax

	# set axis center value
	center_axis_x = 0
	center_axis_y = 0

	Axis = vjoyAxis(0, 0, 0, axis_min, axis_min)
	State = vjoyState(False, False, False, False)
	Sens = vjoySensitive(15.0, 0.7, 0.9, 1.9)

	screen_width = 1980
	screen_height = 1080
	screen_center_x = screen_width / 2
	screen_center_y = screen_height / 2


# active vjoy stick
if keyboard.getPressed(Key.Grave):
	enabled = not enabled
	toggle_enabled(enabled)

if enabled and mouse.rightButton:
	reset_axis_pos()

# throttle modifier
throttle_both = keyboard.getKeyDown(Key.RightShift)
throttle_left = keyboard.getKeyDown(Key.RightAlt)
throttle_right = keyboard.getKeyDown(Key.RightControl)


# stick
if State.stick :
	Axis.x += mouse.deltaX*Sens.x*Sens.mou*0.48
	Axis.y += mouse.deltaY*Sens.y*Sens.mou

	# 计算轴位置的百分比 (-100% 到 100%)
	x_percent = (Axis.x / axis_max) * 100
	y_percent = (Axis.y / axis_max) * 100

    # 将百分比转换为屏幕坐标
	screen_x = screen_center_x + (x_percent / 100) * (screen_width / 2)
	screen_y = screen_center_y + (y_percent / 100) * (screen_height / 2)

    # 设置鼠标位置
	ctypes.windll.user32.SetCursorPos(int(screen_x), int(screen_y))

# throttle
if State.th :
	"""
	if mouse.wheelUp :
		keyboard.setKeyDown(Key.NumberPadPlus)
	elif mouse.wheelDown :
		keyboard.setKeyDown(Key.NumberPadMinus)
	"""
	if throttle_both:
		if Axis.th_l > Axis.th_r :
			Axis.th_r = Axis.th_l
		else:
			Axis.th_l = Axis.th_r
		Axis.th_l += wheel_th(Sens.mou, Sens.th)
		Axis.th_r += wheel_th(Sens.mou, Sens.th)
	if throttle_left:
		Axis.th_l += wheel_th(Sens.mou, Sens.th)
	if throttle_right:
		Axis.th_r += wheel_th(Sens.mou, Sens.th)


# vjoy botton
if State.btn :
	# note: botton number begin with 0
	vJoy[0].setButton(8, mouse.getPressed(2))


# axis value overflow protection
check_overflow(Axis.x, axis_min, axis_max)
check_overflow(Axis.y, axis_min, axis_max)
check_overflow(Axis.th_l, axis_min, axis_max)
check_overflow(Axis.th_r, axis_min, axis_max)


# map axis to vjoy
vJoy[0].x = int(round(Axis.x))
vJoy[0].y = Axis.y
vJoy[0].slider = Axis.th_l
vJoy[0].dial = Axis.th_r
