from ImageProcess.Objects.Components.ArrowWarning import ArrowWarning
from ImageProcess.Objects.Components.Background import Background
from ImageProcess.Objects.Components.Scorebar import Scorebar
from ImageProcess.Objects.Components.Sections import Sections
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
from ImageProcess.PrepareFrames.Components.ArrowWarning import prepare_arrowwarning
from ImageProcess.PrepareFrames.Components.Button import prepare_scoreentry, prepare_inputoverlaybg, \
	prepare_inputoverlay
from ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursortrail, prepare_cursormiddle
from ImageProcess.PrepareFrames.Components.Followpoints import prepare_fpmanager
from ImageProcess.PrepareFrames.Components.Background import prepare_background
from ImageProcess.PrepareFrames.Components.Scorebar import prepare_scorebar
from ImageProcess.PrepareFrames.Components.Sections import prepare_sections
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
from global_var import Settings, Paths


class PreparedFrames:
	def __init__(self, skin, check, beatmap, hd):
		self.cursor, default = prepare_cursor(Settings.scale)
		self.cursormiddle, self.continuous = prepare_cursormiddle(Settings.scale, default)
		self.cursor_trail = prepare_cursortrail(Settings.scale, self.continuous)
		self.scoreentry = prepare_scoreentry(Settings.scale, skin.colours["InputOverlayText"])
		self.inputoverlayBG = prepare_inputoverlaybg(Settings.scale)
		self.key = prepare_inputoverlay(Settings.scale, [255, 220, 20], 2)
		self.mouse = prepare_inputoverlay(Settings.scale, [220, 0, 220], 1)
		self.scorenumbers = ScoreNumbers(Settings.scale)
		self.hitcirclenumber = prepare_hitcirclenumber(beatmap.diff, Settings.playfieldscale)
		self.accuracy = prepare_accuracy(self.scorenumbers)
		self.combocounter = prepare_combo(self.scorenumbers)
		self.hitresult = prepare_hitresults(Settings.scale, beatmap)
		self.spinbonus = prepare_spinbonus(self.scorenumbers)
		self.scorecounter = prepare_scorecounter(self.scorenumbers)
		self.urbar = prepare_bar(Settings.scale, check.scorewindow)
		self.fpmanager = prepare_fpmanager(Settings.playfieldscale)
		self.circle = prepare_circle(beatmap, Settings.playfieldscale, skin, hd)
		self.slider = prepare_slider(beatmap.diff, Settings.playfieldscale, skin)
		self.spinner = prepare_spinner(Settings.playfieldscale)
		self.bg = prepare_background(Paths.beatmap + beatmap.bg[2])
		self.sections = prepare_sections(Settings.scale)
		self.scorebar = prepare_scorebar(Settings.scale)
		self.arrowwarning = prepare_arrowwarning(Settings.scale)


class FrameObjects:
	def __init__(self, frames, skin, beatmap, check, hd):
		opacity_interval, timepreempt, _ = calculate_ar(beatmap.diff["ApproachRate"])

		self.cursormiddle = Cursor(frames.cursormiddle)
		self.cursor = Cursor(frames.cursor)
		self.cursor_trail = Cursortrail(frames.cursor_trail, frames.continuous)
		# self.lifegraph = LifeGraph(skin_path + "scorebar-colour")

		self.scoreentry = ScoreEntry(frames.scoreentry)

		self.inputoverlayBG = InputOverlayBG(frames.inputoverlayBG)
		self.key1 = InputOverlay(frames.key, self.scoreentry)
		self.key2 = InputOverlay(frames.key, self.scoreentry)
		self.mouse1 = InputOverlay(frames.mouse, self.scoreentry)
		self.mouse2 = InputOverlay(frames.mouse, self.scoreentry)

		self.accuracy = Accuracy(frames.accuracy, skin.fonts["ScoreOverlap"])
		self.timepie = TimePie(Settings.scale, self.accuracy)
		self.hitresult = HitResult(frames.hitresult)
		self.spinbonus = SpinBonusScore(frames.spinbonus, skin.fonts["ScoreOverlap"])
		self.combocounter = ComboCounter(frames.combocounter, skin.fonts["ScoreOverlap"])
		self.scorecounter = ScoreCounter(frames.scorecounter, beatmap.diff, skin.fonts["ScoreOverlap"])

		self.urbar = URBar(frames.urbar)

		self.followpoints = FollowPointsManager(frames.fpmanager)

		self.hitcirclenumber = Number(frames.hitcirclenumber, skin.fonts)
		self.circle = CircleManager(frames.circle, timepreempt, self.hitcirclenumber)
		self.slider = SliderManager(frames.slider, beatmap.diff, skin, hd)
		self.spinner = SpinnerManager(frames.spinner)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2])

		self.background = Background(frames.bg, beatmap.start_time - timepreempt)
		self.sections = Sections(frames.sections)
		self.scorebar = Scorebar(frames.scorebar)
		self.arrowwarning = ArrowWarning(frames.arrowwarning)
