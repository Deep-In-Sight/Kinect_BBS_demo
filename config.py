scenario = [
[0, 1, 2, 3, 4], 
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4],
[0, 1, 2, 3, 4]
]


CFG_30cm = {
	"ir_minval": 0,
	"ir_maxval": 2047,
	"depth_minval": 64,
	"depth_maxval": 1023
}


CFG_50cm = {
	"ir_minval": 0,
	"ir_maxval": 4095,
	"depth_minval" : 128,
	"depth_maxval" : 2047
}




class Config():
	def __init__(self):
		self.cfg_30cm = CFG_30cm
		self.cfg_50cm = CFG_50cm
		self.scenario = scenario
		self.correction = 0
		self.Angle = 'd' # 'L' : Left, 'F' : Front, 'R' : Right
		self.Locale = 'G1'
		self.minRecordFrame = 20 	# images / marker position
		self.minRecordTime = 2	# sec / marker position
		self.GYRO = [0,0,0] # GYRO X/Y/Z