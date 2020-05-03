from ImageProcess.Objects.Scores.ScoreNumbers import ScoreNumbers
from ImageProcess.Objects.Components.Followpoints import FollowPointsManager
from ImageProcess.Objects.Components.TimePie import TimePie
from ImageProcess.Objects.HitObjects.CircleNumber import Number
from ImageProcess.Objects.HitObjects.Slider import SliderManager
from ImageProcess.Objects.HitObjects.Spinner import SpinnerManager
from ImageProcess.Objects.Scores.Accuracy import Accuracy
from ImageProcess.Objects.Scores.ComboCounter import ComboCounter
from ImageProcess.Objects.Scores.Hitresult import HitResult
from ImageProcess.Objects.Scores.ScoreCounter import ScoreCounter
from ImageProcess.Objects.HitObjects.Circles import CircleManager
from ImageProcess.Objects.HitObjects.Manager import HitObjectManager
from ImageProcess.Objects.Components.Button import InputOverlay, InputOverlayBG, ScoreEntry
from ImageProcess.Objects.Components.Cursor import Cursor, Cursortrail
from ImageProcess.Objects.Scores.SpinBonusScore import SpinBonusScore
from ImageProcess.Objects.Scores.URBar import URBar
from ImageProcess.PrepareFrames.Components.Button import prepare_scoreentry, prepare_inputoverlaybg, \
	prepare_inputoverlay
from ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursortrail
from ImageProcess.PrepareFrames.Components.Followpoints import prepare_fpmanager
from ImageProcess.PrepareFrames.HitObjects.CircleNumber import prepare_hitcirclenumber
from ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle, calculate_ar
from ImageProcess.PrepareFrames.HitObjects.Slider import prepare_slider
from ImageProcess.PrepareFrames.HitObjects.Spinner import prepare_spinner
from ImageProcess.PrepareFrames.Scores.Accuracy import prepare_accuracy
from ImageProcess.PrepareFrames.Scores.ComboCounter import prepare_combo
from ImageProcess.PrepareFrames.Scores.Hitresult import prepare_hitresults
from ImageProcess.PrepareFrames.Scores.ScoreCounter import prepare_scorecounter
from ImageProcess.PrepareFrames.Scores.SpinBonusScore import prepare_spinbonus
from ImageProcess.PrepareFrames.Scores.URBar import prepare_bar


class PreparedFrames:
	def __init__(self, skin, check, beatmap, settings):
		self.cursor = prepare_cursor(settings.scale)
		self.cursor_trail = prepare_cursortrail(settings.scale)
		self.scoreentry = prepare_scoreentry(settings.scale, skin.colours["InputOverlayText"])
		self.inputoverlayBG = prepare_inputoverlaybg(settings.scale)
		self.key = prepare_inputoverlay(settings.scale, [255, 255, 0])
		self.mouse = prepare_inputoverlay(settings.scale, [255, 0, 255])
		self.scorenumbers = ScoreNumbers(settings.scale)
		self.hitcirclenumber = prepare_hitcirclenumber(beatmap.diff, settings.playfieldscale)
		self.accuracy = prepare_accuracy(self.scorenumbers)
		self.combocounter = prepare_combo(self.scorenumbers)
		self.hitresult = prepare_hitresults(settings.scale)
		self.spinbonus = prepare_spinbonus(self.scorenumbers)
		self.scorecounter = prepare_scorecounter(self.scorenumbers)
		self.urbar = prepare_bar(settings.scale, check.scorewindow)
		self.fpmanager = prepare_fpmanager(settings.playfieldscale)
		self.circle = prepare_circle(beatmap, settings.playfieldscale, skin, settings.fps)
		self.slider = prepare_slider(beatmap.diff, settings.playfieldscale, skin, settings.fps)
		self.spinner = prepare_spinner(settings.playfieldscale)


class FrameObjects:
	def __init__(self, frames, skin, beatmap, check, settings):
		opacity_interval, timepreempt, _ = calculate_ar(beatmap.diff["ApproachRate"], settings.fps)

		self.cursor = Cursor(frames.cursor)
		self.cursor_trail = Cursortrail(frames.cursor_trail)
		# self.lifegraph = LifeGraph(skin_path + "scorebar-colour")

		self.scoreentry = ScoreEntry(frames.scoreentry)

		self.inputoverlayBG = InputOverlayBG(frames.inputoverlayBG)
		self.key1 = InputOverlay(frames.key, self.scoreentry)
		self.key2 = InputOverlay(frames.key, self.scoreentry)
		self.mouse1 = InputOverlay(frames.mouse, self.scoreentry)
		self.mouse2 = InputOverlay(frames.mouse, self.scoreentry)

		self.accuracy = Accuracy(frames.accuracy, skin.fonts["ScoreOverlap"], settings)
		self.timepie = TimePie(settings.scale, self.accuracy)
		self.hitresult = HitResult(frames.hitresult, settings)
		self.spinbonus = SpinBonusScore(frames.spinbonus, skin.fonts["ScoreOverlap"], settings)
		self.combocounter = ComboCounter(frames.combocounter, skin.fonts["ScoreOverlap"], settings)
		self.scorecounter = ScoreCounter(frames.scorecounter, beatmap.diff, skin.fonts["ScoreOverlap"], settings)

		self.urbar = URBar(frames.urbar, settings)

		self.followpoints = FollowPointsManager(frames.fpmanager, settings)

		self.hitcirclenumber = Number(frames.hitcirclenumber, skin.fonts, opacity_interval)
		self.circle = CircleManager(frames.circle, timepreempt, self.hitcirclenumber)
		self.slider = SliderManager(frames.slider, beatmap.diff, skin, settings)
		self.spinner = SpinnerManager(frames.spinner, settings)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2])
