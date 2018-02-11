#
#	Proportionally shifting subs from one timestamps offset and rate to another
#	Heavily used by https://vk.com/teamnotdead releases
#
#	Usage: subshift.py shift.cfg, where shift.cfg structure is:
#	----------
#	source.srt
#	target.srt
#	N1	NewTimestamp1 (hh:mm:ss,ms or hh:mm:ss.ms)
#	...
#	Nk	NewTimestampK
#	----------
#
#   Sample:
#	StarTrek.Discovery.S01E14.WEBRip.TeamNotDead.srt
#	Star.Trek.Discovery.S01E14.The.War.Without.The.War.Within.1080p.NF.WEBRip.DD5.1.x264-NTb.srt
#	1	00:00:12,011
#	182	0:10:05.605
#	184	0:11:43.828
#	370	0:22:50.452
#	795	00:47:29,930
#	796	0:47:55.331 
#


import sys
import re

class SubTime:
	ts = 0
	sts = None

	def __init__(self, s, st = None):
		self.set(s)
		sts = st

	def set(self, s):
		m = re.search("(\d+)\:(\d+)\:(\d+)[\,\.](\d+)", s)
		self.ts = int(m[4])+int(m[3])*1000+int(m[2])*60000+int(m[1])*3600000

	def getshifted(self, o1, o2, k):
		return int((self.ts-o1)*k+o2)
		
	def get(self, o1=0, o2=0, k=1):
		if self.sts:
			t = self.sts.getshifted(o1, o2, k) + (self.ts-self.sts.ts)
		else:
			t = self.getshifted(o1, o2, k)
		return '{:0>2}:{:0>2}:{:0>2},{:0>3}'.format(t//3600000, (t % 3600000) // 60000, (t % 60000) // 1000, t % 1000)

	def __str__(self):
		return self.get()

class SubTitle:
	bInit = False
	nTitle = 0
		
	def __init__(self, f):
		while True:
			s = f.readline()
			if not s:
				raise Exception()
			if re.search("\d+\s+\-\-\>\s+\d+", s):
				break
			if(int(s) > 0):
				self.nTitle = int(s)
		else:
			return
		m = re.search("(.+) \-\-\> (.+)", s)
		self.start = SubTime(m[1])
		self.end = SubTime(m[2])
#		self.end = SubTime(m[2], self.start)
		self.lines = []
		while True:
			s = f.readline()
			if not s or s == '\n':
				break
			self.lines.append(s)
		self.bInit = True
		
	def get(self, o1=0, o2=0, k=1):
		s = self.start.get(o1, o2, k) + ' --> ' + self.end.get(o1, o2, k) + '\n'
		for l in self.lines:
			s += l
		return s

	def __str__(self):
		return self.get()
		
def PrintSubTitles(f, SubTitles, kp1, kp2):
	src1 = SubTitles[kp1[0]].start
	src2 = SubTitles[kp2[0]].start
	
	k = (kp2[1].ts-kp1[1].ts)/(src2.ts-src1.ts)
	
	for i,s in SubTitles.items():
		if (s.nTitle == kp1[0]) and i>1:
			continue
		if (s.nTitle < kp1[0]) or (s.nTitle > kp2[0]):
			continue
		f.write(str(s.nTitle)+"\n"+s.get(src1.ts, kp1[1].ts, k)+"\n")
	
def PrintFinalSubTitles(f, SubTitles, kp):
	src = SubTitles[kp[0]].start
	
	for i,s in SubTitles.items():
		if (s.nTitle == kp[0]) and i>1:
			continue
		if (s.nTitle < kp[0]):
			continue
		f.write(str(s.nTitle)+"\n"+s.get(src.ts, kp[1].ts, 1)+"\n")

def main():
	if len(sys.argv) < 2:
		print('Usage: ' + sys.argv[0] + ' config.cfg')
		return

	SubTitles = {}
	KeyPoints = []

	with open(sys.argv[1]) as fcfg:
		sfName = fcfg.readline().rstrip()
		rfName = fcfg.readline().rstrip()
	
		while True:
			s = fcfg.readline()
			if not s or s == '\n':
				break
			(n, ts) = s.split()
			KeyPoints.append((int(n), SubTime(ts)))

	with open(sfName, encoding='utf-8-sig') as f:
		try:
			while True:
				st = SubTitle(f)
				if st.bInit:
					SubTitles[st.nTitle] = st
		except:
			pass

	with open(rfName, "wt", encoding='utf-8-sig') as f:
		for i,kp in enumerate(KeyPoints):
			if i < len(KeyPoints)-1:
				PrintSubTitles(f, SubTitles, KeyPoints[i], KeyPoints[i+1])
			else:
				PrintFinalSubTitles(f, SubTitles, KeyPoints[-1])
		
		
main()
