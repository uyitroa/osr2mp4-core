import json

import requests
from recordclass import recordclass
import re
from ... import imageproc
from ..FrameObject import FrameObject
from ...PrepareFrames.Components.Text import prepare_text
from ....Parser.scoresparser import getscores
from itertools import compress
from itertools import product

BoardInfo = recordclass("BoardInfo", "score maxcombo intscore intcombo playername x y alpha id")


def getsummods(mods):
	if mods == "*" or mods == "":
		return "*"
	mods = re.findall('..', mods)
	modidct = {
		"NM": 0,
		"NF": 1,
		"EZ": 2,
		"HD": 8,
		"HR": 16,
		"SD": 32,
		"DT": 64,
		"RX": 128,
		"HT": 256,
		"NC": 576,
		"FL": 1024,
		"AT": 2048,
		"SO": 4096,
		"AP": 8192,
		"PF": 16384
	}

	summod = 0

	for i in mods:
		summod += modidct[i]

	return summod


# Mod's string should be splitted to required mods and optional mods


def mod_to_list(mods):
	required_mods = ""
	optional_mods = []
	i = 0
	j = 0
	while i < len(mods):
		if mods[i] == "(":
			j = i
			while mods[j] != ")":
				j += 1
			optional_mods.append(mods[i + 1:j])
			i = j + 1
		else:
			required_mods += mods[i:i + 2]
			i += 2
	return required_mods, optional_mods


def solve(mod):
	return (list(compress(mod, mask)) for mask in product(*[[0, 1]] * len(mod)))


def getmods(mods):
	if mods == "*":
		return "*"
	allmods = []
	required_mods, optional_mods = mod_to_list(mods)
	for i in solve(optional_mods):
		output = required_mods + "".join(i)
		if output == "":
			allmods.append("NM")
		else:
			allmods.append(output)
	return allmods


class Scoreboard(FrameObject):
	def __init__(self, frames, scorenetryframes, effectframes, replay_info, beatmap, settings):
		FrameObject.__init__(self, frames, settings=settings)

		self.score = scorenetryframes[0]
		self.rank = scorenetryframes[1]
		self.combo = scorenetryframes[2]

		self.effecteclipse = effectframes[0]
		self.effectcircle = effectframes[1]
		self.effectx, self.effecty, self.effectalpha = [], [], []

		self.scoreboards = []
		self.posboards = []
		self.alphaboards = None
		self.origposboards = []
		self.playerboard = None
		self.curscore = 0
		self.maxcombo = 0
		self.oldrankid = None
		self.falling = False
		self.removeone = 0

		self.nboard = 6
		self.height = (660 - 313) / self.nboard * settings.scale
		self.beatmaphash = replay_info.beatmap_hash
		self.playerscore = replay_info.score
		self.playername = replay_info.player_name
		self.beatmapid = beatmap.meta.get("BeatmapID", -1)

		self.scoresid = []
		self.getscores()

		if len(self.scoreboards) > 50 - self.removeone:
			_, _ = self.sortscore(000)
			self.scoreboards = self.scoreboards[:50 - self.removeone]
		self.scoreboards.append(BoardInfo("0", "0", self.curscore, self.maxcombo, replay_info.player_name, None, None, None, -1))
		self.shows = max(0, len(self.scoreboards)-self.nboard+1)
		_, self.currank = self.sortscore()

		self.setuppos()

		self.animate = False


		playernames = [x.playername for x in self.scoreboards]
		self.nameimg = prepare_text(playernames, 18 * self.settings.scale, (255, 255, 255, 255), self.settings, 0.5)
		playertext = prepare_text([self.playername], 18 * self.settings.scale, (255, 255, 255, 255), self.settings, 1)

		self.nameimg[self.playername] = playertext[self.playername]

	def setuppos(self):
		x = 0
		y = 313 * self.settings.scale
		self.nboard = min(self.nboard, len(self.scoreboards))
		for i in range(self.nboard):
			self.origposboards.append([x, y])
			y += self.height
		self.alphaboards = [1] * self.nboard

		for i in range(len(self.scoreboards)-1, -1, -1):
			if i <= len(self.scoreboards) - self.nboard and len(self.scoreboards) - self.nboard >= 0 and len(self.origposboards) > 1:
				x, y = self.origposboards[1]
				alpha = 0
			else:
				index = i - len(self.scoreboards) + self.nboard
				x, y = self.origposboards[index]
				alpha = 1
			self.scoreboards[i].x = x
			self.scoreboards[i].y = y
			self.scoreboards[i].alpha = alpha
		self.scoreboards[0].x = self.origposboards[0][0]
		self.scoreboards[0].y = self.origposboards[0][1]
		self.scoreboards[0].alpha = 1

	def getscores(self):
		mods = getmods(self.settings.settings["Mods leaderboard"])

		for mod in mods:
			if self.settings.settings["Global leaderboard"]:
				self.getglobalscores(mod)
			else:
				self.getlocalscores(mod)

	def getglobalscores(self, mods):
		k = self.settings.settings["api key"]
		if k is None:
			print("\n\n YOU DID NOT ENTERED THE API KEY. GET THE API HERE https://osu.ppy.sh/p/api/\n\n")
			self.getlocalscores(mods)
			return


		if mods == "*":
			data = {'k': k, 'b': self.beatmapid}
		else:
			summods = getsummods(mods)
			data = {'k': k, 'b': self.beatmapid, 'mods': summods}


		r = requests.post("https://osu.ppy.sh/api/get_scores", data=data)
		try:
			data = json.loads(r.text)
		except json.decoder.JSONDecodeError:
			return

		if "error" in data:
			print("\n\n {} \n\n".format(data["error"]))
			self.getlocalscores(mods)
			return

		for i in range(len(data)):
			score = data[i]

			if score["username"] == self.playername:
				if int(score["score"]) == self.playerscore:
					self.removeone = 1
				continue

			if len(score["username"]) > 13:
				score["username"] = score["username"][:13] + ".."

			keepgoing = self.filter(score["user_id"],  int(score["score"]))

			if not keepgoing:
				continue

			strscore = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score["score"]))  # add dot to every 3 digits
			strcombo = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score["maxcombo"]))
			self.scoreboards.append(BoardInfo(strscore, strcombo, int(score["score"]), int(score["maxcombo"]), score["username"], None, None, None, i))
		self.oldrankid = None


	def getlocalscores(self, mods):
		try:
			scores = getscores(self.beatmaphash, self.settings.osu + "scores.db")
		except Exception:
			return

		for i in range(len(scores["scores"])):
			score = scores["scores"][i]

			if int(score["score"]) == self.playerscore and score["player"] == self.playername:
				continue

			summods = getsummods(mods)
			if summods != score["mods"]["modFlags"] and summods != "*":
				continue

			strscore = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score["score"]))  # add dot to every 3 digits
			strcombo = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score["max_combo"]))
			self.scoreboards.append(BoardInfo(strscore, strcombo, score["score"], score["max_combo"], score["player"], None, None, None, i))
		self.oldrankid = None

	def sortscore(self, playerrank=None):
		self.scoreboards.sort(key=lambda x: x.intscore, reverse=True)
		if playerrank is None:
			playerrank = [i for i in range(len(self.scoreboards)) if self.scoreboards[i].id == -1][0]

		if self.oldrankid == playerrank:
			return False, playerrank
		self.oldrankid = playerrank
		return True, playerrank

	def setscore(self, score, combo=None):
		self.curscore = score
		curinfo = self.scoreboards[self.currank]
		if combo is not None:
			combo = max(combo, curinfo.intcombo)
		else:
			combo = curinfo.intcombo
		strscore = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score))  # add dot to every 3 digits
		strcombo = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(combo))
		self.scoreboards[self.currank] = BoardInfo(strscore, strcombo, score, combo, curinfo.playername, curinfo.x, curinfo.y, curinfo.alpha, -1)
		self.animate, self.currank = self.sortscore()

		if self.animate:
			self.effectalpha.append(2.5)
			self.effectx.append(-500 * self.settings.scale)
			self.effecty.append(curinfo.y)

	def setsetscore(self, score, combo):
		self.curscore = score
		curinfo = self.scoreboards[self.currank]
		if combo is not None:
			combo = max(combo, curinfo.intcombo)
		else:
			combo = curinfo.intcombo
		strscore = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(score))  # add dot to every 3 digits
		strcombo = re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(combo))
		self.scoreboards[self.currank] = BoardInfo(strscore, strcombo, score, combo, curinfo.playername, curinfo.x, curinfo.y, curinfo.alpha, -1)
		self.animate, self.currank = self.sortscore()


		if self.animate:
			self.setrankpos()
			self.effectalpha.append(2.5)
			self.effectx.append(-500 * self.settings.scale)
			self.effecty.append(curinfo.y)

	def getrange(self):
		if self.currank < self.nboard - 1:
			return 0, min(6, self.nboard)
		return self.currank - 4, self.currank

	def setranktoanimate(self, prevrank=None):
		start, end = self.getrange()
		self.scoreboards[0].y = self.origposboards[0][1]
		count = 0
		for i in range(start+1, end):
			count += 1
			if i == self.currank:
				continue
			self.scoreboards[i].y = self.origposboards[count][1]
		if prevrank is None:
			prevrank = self.currank+1
		rank = max(prevrank-1, self.currank)
		rank = min(self.nboard - 2, rank)
		if self.currank < self.nboard - 1:
			self.scoreboards[self.currank].y = self.origposboards[rank+1][1]
			for i in range(0, self.nboard):
				self.scoreboards[i].alpha = 1

	def setrankpos(self):
		start, end = self.getrange()
		self.scoreboards[0].y = self.origposboards[0][1]
		count = 0
		for i in range(start + 1, end):
			count += 1
			if i == self.currank:
				continue
			self.scoreboards[i].y = self.origposboards[count][1]

		if self.currank < self.nboard - 1:
			self.scoreboards[self.currank].y = self.origposboards[self.currank][1]
			for i in range(0, self.nboard):
				self.scoreboards[i].alpha = 1

	def drawnumber(self, background, x_offset, y_offset, number, frames, alpha):
		if number == "0":
			return
		number = number
		x_start = x_offset
		for digit in number:
			if digit == "x":
				digit = 10
			elif digit == ".":
				digit = 11
			else:
				digit = int(digit)
			imageproc.add(frames[digit], background, x_start, y_offset + self.height * 0.8, alpha=alpha)
			x_start += frames[digit].size[0]

	def drawscore(self, background, y_offset, number, alpha):
		self.drawnumber(background, 5 * self.settings.scale, y_offset, number, self.score, alpha)

	def drawcombo(self, background, y_offset, number, alpha):
		if number == "0":
			return
		number = number + "x"
		n = len(number)
		x_start = self.frames[0].size[0] * 0.95 - int(n * self.combo[0].size[0])
		self.drawnumber(background, x_start, y_offset, number, self.combo, alpha)

	def drawname(self, background, y_offset, text, alpha):
		imageproc.add(self.nameimg[text], background, 0, y_offset + self.height * 0.15, alpha, topleft=True)

	def add_to_frame(self, np_img, background, in_break):
		if not self.settings.settings["Show scoreboard"]:
			return

		shows = max(1, self.currank - self.nboard + 2)
		ranktoclimb = self.nboard - 1
		for x in range(len(self.scoreboards)-1, -1, -1):
			if shows <= x < self.currank:
				boardindex = x - shows + 1
				if self.scoreboards[x].y >= self.origposboards[boardindex][1] and self.scoreboards[x].alpha >= 1:
					self.scoreboards[x].y = self.origposboards[boardindex][1]
				else:
					coef = (self.scoreboards[x].y - self.origposboards[boardindex][1]) / self.scoreboards[x].y
					if coef >= 0:
						step = max(1, 30 * coef)
					elif coef < 0:
						step = min(-1, 30 * coef)
					else:
						step = 0
					self.scoreboards[x].y = min(self.origposboards[boardindex][1], self.scoreboards[x].y - step)
					self.scoreboards[x].alpha = min(1, self.scoreboards[x].alpha + 0.02)

			if self.currank < ranktoclimb and self.currank < x < self.nboard:
				coef = (self.scoreboards[x].y - self.origposboards[x][1]) / self.scoreboards[x].y
				if coef > 0:
					step = max(1, 30 * coef)
				elif coef < 0:
					step = min(-1, 30 * coef)
				else:
					step = 0
				self.scoreboards[x].y = min(self.scoreboards[x].y - step, self.origposboards[x][1])
				self.scoreboards[x].alpha = min(1, self.scoreboards[x].alpha + 0.02)

			if self.scoreboards[x].alpha <= 0 or (self.currank < ranktoclimb < x):
				continue

			if ranktoclimb <= self.currank < x:
				# fadeout and fall
				self.scoreboards[x].alpha -= 0.05
				self.scoreboards[x].y += 10

			if x == self.currank:
				self.frame_index = 1
				boardindex = min(ranktoclimb, self.currank)
				coef = (self.scoreboards[x].y - self.origposboards[boardindex][1]) / self.scoreboards[x].y
				step = max(1, 30 * coef)
				self.scoreboards[x].y = max(self.scoreboards[x].y - step, self.origposboards[boardindex][1])

				# alpha = self.scoreboards[x].alpha
			else:
				self.frame_index = 0
				# alpha = self.scoreboards[x].alpha * 0.7

			if self.settings.settings["In-game interface"] or in_break:
				if self.scoreboards[x].alpha > 0:
					super().add_to_frame(background, self.scoreboards[x].x, self.scoreboards[x].y, topleft=True, alpha=self.scoreboards[x].alpha)
					self.drawscore(background, self.scoreboards[x].y, self.scoreboards[x].score, alpha=self.scoreboards[x].alpha)
					self.drawcombo(background, self.scoreboards[x].y, self.scoreboards[x].maxcombo,alpha=self.scoreboards[x].alpha)
					self.drawname(background, self.scoreboards[x].y, self.scoreboards[x].playername, alpha=self.scoreboards[x].alpha)

		for i in range(len(self.effectalpha)-1, -1, -1):
			alpha = max(0, min(1, self.effectalpha[i]))
			if self.settings.settings["In-game interface"] or in_break:
				imageproc.add(self.effecteclipse, background, self.effectx[i], self.effecty[i], alpha=alpha)
				imageproc.add(self.effectcircle, background, 0, self.effecty[i], alpha=alpha)

				self.effectalpha[i] -= 0.075
				self.effectx[i] = min(0, self.effectx[i] + 40 * self.settings.scale * (-self.effectx[i])/350)  # big brain formula

				if self.effectalpha[i] <= 0:
					del self.effectalpha[i]
					del self.effectx[i]
					del self.effecty[i]

	def filter(self, userid, score):
		try:
			idindex = self.scoresid.index(userid)
			if score > self.scoreboards[idindex].intscore:
				del self.scoresid[idindex]
				del self.scoreboards[idindex]
				return True
			return False
		except ValueError:
			self.scoresid.append(userid)
			return True

