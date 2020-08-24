import logging
import os

from osr2mp4.ImageProcess.PrepareFrames.Scores.URArrow import prepare_urarrow
from osr2mp4.ImageProcess.Objects.Components.Flashlight import Flashlight
from osr2mp4.ImageProcess.PrepareFrames.Components.Flashlight import prepare_flashlight
from osr2mp4.ImageProcess.Objects.Components.PlayingModIcons import PlayingModIcons
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingUR import prepare_rankingur
from osr2mp4.ImageProcess.Objects.Scores.HitresultCounter import HitresultCounter
from osr2mp4.osrparse.enums import Mod

from osr2mp4.ImageProcess.Objects.Scores.PPCounter import PPCounter
from osr2mp4.ImageProcess.PrepareFrames.Components.PlayingGrade import prepare_playinggrade
from osr2mp4.ImageProcess.Objects.Components.PlayingGrade import PlayingGrade
from osr2mp4.CheckSystem.Judgement import DiffCalculator
from osr2mp4.ImageProcess.Objects.RankingScreens.Menuback import Menuback
from osr2mp4.ImageProcess.Objects.RankingScreens.ModIcons import ModIcons
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingAccuracy import RankingAccuracy
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingCombo import RankingCombo
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingGrade import RankingGrade
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingGraph import RankingGraph
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingHitresults import RankingHitresults
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingPanel import RankingPanel
from osr2mp4.ImageProcess.Objects.Components.Scoreboard import Scoreboard
from osr2mp4.ImageProcess.Objects.Components.ArrowWarning import ArrowWarning
from osr2mp4.ImageProcess.Objects.Components.Background import Background
from osr2mp4.ImageProcess.Objects.Components.Scorebar import Scorebar
from osr2mp4.ImageProcess.Objects.Components.ScorebarBG import ScorebarBG
from osr2mp4.ImageProcess.Objects.Components.Sections import Sections
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingReplay import RankingReplay
from osr2mp4.ImageProcess.Objects.RankingScreens.RankingTitle import RankingTitle
from osr2mp4.ImageProcess.Objects.Scores.ScoreNumbers import ScoreNumbers
from osr2mp4.ImageProcess.Objects.Components.Followpoints import FollowPointsManager
from osr2mp4.ImageProcess.Objects.Components.TimePie import TimePie
from osr2mp4.ImageProcess.Objects.HitObjects.CircleNumber import Number
from osr2mp4.ImageProcess.Objects.HitObjects.Slider import SliderManager
from osr2mp4.ImageProcess.Objects.HitObjects.Spinner import SpinnerManager
from osr2mp4.ImageProcess.Objects.Scores.Accuracy import Accuracy
from osr2mp4.ImageProcess.Objects.Scores.ComboCounter import ComboCounter
from osr2mp4.ImageProcess.Objects.Scores.Hitresult import HitResult
from osr2mp4.ImageProcess.Objects.Scores.ScoreCounter import ScoreCounter
from osr2mp4.ImageProcess.Objects.HitObjects.Circles import CircleManager
from osr2mp4.ImageProcess.Objects.HitObjects.Manager import HitObjectManager
from osr2mp4.ImageProcess.Objects.Components.Button import InputOverlay, InputOverlayBG, ScoreEntry
from osr2mp4.ImageProcess.Objects.Components.Cursor import Cursor, Cursortrail
from osr2mp4.ImageProcess.Objects.Scores.SpinBonusScore import SpinBonusScore
from osr2mp4.ImageProcess.Objects.Scores.URBar import URBar
from osr2mp4.ImageProcess.PrepareFrames.Components.ArrowWarning import prepare_arrowwarning
from osr2mp4.ImageProcess.PrepareFrames.Components.Button import prepare_scoreentry, prepare_inputoverlaybg, \
	prepare_inputoverlay
from osr2mp4.ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursortrail, prepare_cursormiddle
from osr2mp4.ImageProcess.PrepareFrames.Components.Followpoints import prepare_fpmanager
from osr2mp4.ImageProcess.PrepareFrames.Components.Background import prepare_background
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.BackButton import prepare_menuback
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.ModIcons import prepare_modicons
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingAccuracy import prepare_rankingaccuracy
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingCombo import prepare_rankingcombo
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingGrade import prepare_rankinggrade
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingGraph import prepare_rankinggraph
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingHitresults import prepare_rankinghitresults
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingPanel import prepare_rankingpanel
from osr2mp4.ImageProcess.PrepareFrames.Components.Scorebar import prepare_scorebar
from osr2mp4.ImageProcess.PrepareFrames.Components.ScorebarBG import prepare_scorebarbg
from osr2mp4.ImageProcess.PrepareFrames.Components.Scoreboard import prepare_scoreboard
from osr2mp4.ImageProcess.PrepareFrames.Components.Sections import prepare_sections
from osr2mp4.ImageProcess.PrepareFrames.Effects.ScoreboardEffect import prepare_scoreboardeffect
from osr2mp4.ImageProcess.PrepareFrames.HitObjects.CircleNumber import prepare_hitcirclenumber
from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle, calculate_ar
from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Slider import prepare_slider
from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Spinner import prepare_spinner
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingReplay import prepare_rankingreplay
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingScore import prepare_rankingscorecounter
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingTitle import prepare_rankingtitle
from osr2mp4.ImageProcess.PrepareFrames.Scores.Accuracy import prepare_accuracy
from osr2mp4.ImageProcess.PrepareFrames.Scores.ComboCounter import prepare_combo
from osr2mp4.ImageProcess.PrepareFrames.Scores.Hitresult import prepare_hitresults
from osr2mp4.ImageProcess.PrepareFrames.Scores.ScoreCounter import prepare_scorecounter
from osr2mp4.ImageProcess.PrepareFrames.Scores.Scoreentry import prepare_scoreboardscore
from osr2mp4.ImageProcess.PrepareFrames.Scores.SpinBonusScore import prepare_spinbonus
from osr2mp4.ImageProcess.PrepareFrames.Scores.URBar import prepare_bar


class PreparedFrames:
	def __init__(self, settings, diff, mod_combination, ur=None, bg=None, loadranking=True):
		skin = settings.skin_ini
		self.loadranking = loadranking
		check = DiffCalculator(diff)
		hd = Mod.Hidden in mod_combination
		fl = Mod.Flashlight in mod_combination
		if settings.settings["Automatic cursor size"]:
			circlescale = 4/diff["CircleSize"]
			settings.settings["Cursor size"] *= circlescale
		if ur is None:
			ur = [0, 0, 0]
		if bg is None:
			bg = [0, 0, ""]

		logging.debug('start preparing cursor')
		self.cursor, default = prepare_cursor(settings.scale * settings.settings["Cursor size"], settings)
		logging.debug('start preparing cursormiddle')
		self.cursormiddle, self.continuous = prepare_cursormiddle(settings.scale * settings.settings["Cursor size"], settings, default)
		logging.debug('start preparing cursortrail')
		self.cursor_trail = prepare_cursortrail(settings.scale * settings.settings["Cursor size"], self.continuous, settings)

		logging.debug('start preparing scorenetry')
		self.scoreentry = prepare_scoreentry(settings.scale, skin.colours["InputOverlayText"], settings)
		self.inputoverlayBG = prepare_inputoverlaybg(settings.scale, settings)
		self.key = prepare_inputoverlay(settings.scale, [255, 220, 20], 2, settings)
		self.mouse = prepare_inputoverlay(settings.scale, [220, 0, 220], 1, settings)

		logging.debug('start preparing scorenumber')
		self.scorenumbers = ScoreNumbers(settings.scale, settings)
		self.hitcirclenumber = prepare_hitcirclenumber(diff, settings.playfieldscale, settings)

		logging.debug('start preparing accuracy')
		self.accuracy = prepare_accuracy(self.scorenumbers)
		self.combocounter = prepare_combo(self.scorenumbers, settings)
		self.hitresult = prepare_hitresults(settings.scale, diff, settings)
		self.spinbonus = prepare_spinbonus(self.scorenumbers)
		self.scorecounter = prepare_scorecounter(self.scorenumbers)

		self.playinggrade = prepare_playinggrade(settings.scale * 0.75, settings)

		self.urbar = prepare_bar(settings.scale * settings.settings["Score meter size"], check.scorewindow)

		self.fpmanager = prepare_fpmanager(settings.playfieldscale, settings)

		logging.debug('start preparing circle')
		self.circle = prepare_circle(diff, settings.playfieldscale, settings, hd)
		self.slider = prepare_slider(diff, settings.playfieldscale, settings)
		self.spinner = prepare_spinner(settings.playfieldscale, settings)

		logging.debug('start preparing background')
		self.bg = prepare_background(os.path.join(settings.beatmap, bg[2]), settings)

		logging.debug('start preparing sections')
		self.sections = prepare_sections(settings.scale, settings)
		self.scorebarbg = prepare_scorebarbg(settings.scale, self.bg, settings)
		self.scorebar = prepare_scorebar(settings.scale, settings)
		self.arrowwarning = prepare_arrowwarning(settings.scale, settings)

		logging.debug('start preparing scoreboard')
		self.scoreboardscore = prepare_scoreboardscore(settings.scale, settings)
		self.scoreboard = prepare_scoreboard(settings.scale, settings)
		self.scoreboardeffect = prepare_scoreboardeffect(settings.scale)

		self.modicons = prepare_modicons(settings.scale, settings)
		if loadranking:
			self.rankingpanel = prepare_rankingpanel(settings.scale, self.bg, settings)
			self.rankinghitresults = prepare_rankinghitresults(settings.scale, settings)
			self.rankingscore = prepare_rankingscorecounter(self.scorenumbers)
			self.rankinggrades = prepare_rankinggrade(settings.scale, settings)
			self.rankingtitle = prepare_rankingtitle(settings.scale, settings)
			self.rankingcombo = prepare_rankingcombo(settings.scale * 1.05, settings)
			self.rankingaccuracy = prepare_rankingaccuracy(settings.scale * 1.05, settings)
			self.menuback = prepare_menuback(settings.scale, settings)
			self.rankingreplay = prepare_rankingreplay(settings.scale, settings)
			self.rankinggraph = prepare_rankinggraph(settings.scale, settings)
			logging.debug("start preparing ur ranking")
			self.rankingur = prepare_rankingur(settings, ur)
			self.rankinggraph.extend(self.rankingur)

		self.flashlight = prepare_flashlight(settings, fl)
		self.urarrow = prepare_urarrow(settings)
		logging.debug('start preparing done')


class FrameObjects:
	def __init__(self, frames, settings, diff, replay_info, meta, maphash, map_time):
		opacity_interval, timepreempt, _ = calculate_ar(diff["ApproachRate"], settings)
		check = DiffCalculator(diff)
		rankinggap = 0
		skin = settings.skin_ini
		hd = Mod.Hidden in replay_info.mod_combination
		hasfl = Mod.Flashlight in replay_info.mod_combination

		self.cursormiddle = Cursor(frames.cursormiddle)
		self.cursor = Cursor(frames.cursor)
		self.cursor_trail = Cursortrail(frames.cursor_trail, frames.continuous, settings)
		# self.lifegraph = LifeGraph(skin_path + "scorebarbg-colour")

		self.scoreentry = ScoreEntry(frames.scoreentry, settings)

		self.inputoverlayBG = InputOverlayBG(frames.inputoverlayBG, settings=settings)
		self.key1 = InputOverlay(frames.key, self.scoreentry, settings)
		self.key2 = InputOverlay(frames.key, self.scoreentry, settings)
		self.mouse1 = InputOverlay(frames.mouse, self.scoreentry, settings)
		self.mouse2 = InputOverlay(frames.mouse, self.scoreentry, settings)
		self.playingmodicons = PlayingModIcons(frames.modicons, replay_info, settings)

		self.accuracy = Accuracy(frames.accuracy, skin.fonts["ScoreOverlap"], settings)
		self.timepie = TimePie(self.accuracy, map_time[0], map_time[1], frames.scorebarbg, settings)
		self.playinggrade = PlayingGrade(frames.playinggrade, self.timepie, replay_info, settings)
		self.hitresult = HitResult(frames.hitresult, settings, replay_info.mod_combination)
		self.spinbonus = SpinBonusScore(frames.spinbonus, skin.fonts["ScoreOverlap"], settings)
		self.combocounter = ComboCounter(frames.combocounter, skin.fonts["ScoreOverlap"], settings)
		self.scorecounter = ScoreCounter(frames.scorecounter, diff, skin.fonts["ScoreOverlap"], settings)

		self.urbar = URBar(frames.urbar, frames.urarrow, settings)

		self.followpoints = FollowPointsManager(frames.fpmanager, settings)

		self.hitcirclenumber = Number(frames.hitcirclenumber, skin.fonts)
		self.circle = CircleManager(frames.circle, timepreempt, self.hitcirclenumber, settings)
		self.slider = SliderManager(frames.slider, diff, settings, hd)
		self.spinner = SpinnerManager((frames.spinner, frames.scorecounter), settings, check)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2], settings)

		self.background = Background(frames.bg, map_time[0] - timepreempt, settings, hasfl)
		self.sections = Sections(frames.sections, settings)
		self.scorebarbg = ScorebarBG(frames.scorebarbg, map_time[0] - timepreempt, settings, hasfl)
		self.scorebar = Scorebar(frames.scorebar, settings)
		self.arrowwarning = ArrowWarning(frames.arrowwarning, settings)

		self.scoreboard = Scoreboard(frames.scoreboard, frames.scoreboardscore, frames.scoreboardeffect, replay_info, meta, maphash, settings)

		if frames.loadranking:
			self.rankingpanel = RankingPanel(frames.rankingpanel, settings)
			self.rankinghitresults = RankingHitresults(frames.rankinghitresults, replay_info, frames.rankingscore, rankinggap, settings)
			self.rankingtitle = RankingTitle(frames.rankingtitle, replay_info, meta, settings)
			self.rankingcombo = RankingCombo(frames.rankingcombo, replay_info, frames.rankingscore, rankinggap, settings)
			self.rankingaccuracy = RankingAccuracy(frames.rankingaccuracy, replay_info, frames.rankingscore, rankinggap, settings)
			self.rankinggrade = RankingGrade(replay_info, frames.rankinggrades, rankinggap, settings)
			self.menuback = Menuback(frames.menuback, settings)
			self.modicons = ModIcons(frames.modicons, replay_info, settings)
			self.rankingreplay = RankingReplay(frames.rankingreplay, settings)
			self.rankinggraph = RankingGraph(frames.rankinggraph, replay_info, settings)

		self.ppcounter = PPCounter(settings)
		self.hitresultcounter = HitresultCounter(settings)
		self.flashlight = Flashlight(frames.flashlight, settings, hasfl)
