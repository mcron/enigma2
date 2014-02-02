from Tools.Profile import profile
from Tools.BoundFunction import boundFunction

# workaround for required config entry dependencies.
import Screens.MovieSelection
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.Pixmap import MultiPixmap
from Tools.Directories import fileExists

profile("LOAD:enigma")
import enigma
from boxbranding import getBoxType, getMachineBrand

profile("LOAD:InfoBarGenerics")
from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarRdsDecoder, InfoBarRedButton, InfoBarTimerButton, InfoBarVmodeButton, \
	InfoBarEPG, InfoBarSeek, InfoBarInstantRecord, InfoBarINFOpanel, InfoBarResolutionSelection, InfoBarAspectSelection, \
	InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey, \
	InfoBarSubserviceSelection, InfoBarShowMovies, \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions, \
	InfoBarSubtitleSupport, InfoBarPiP, InfoBarPlugins, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom, \
	setResumePoint, delResumePoint

profile("LOAD:InitBar_Components")
from Components.ActionMap import HelpableActionMap
from Components.Timeshift import InfoBarTimeshift
from Components.config import config
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

profile("LOAD:HelpableScreen")
from Screens.HelpMenu import HelpableScreen

class InfoBar(InfoBarBase, InfoBarShowHide,
	InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder,
	InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarINFOpanel, InfoBarResolutionSelection, InfoBarAspectSelection, InfoBarVmodeButton,
	HelpableScreen, InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarUnhandledKey,
	InfoBarSubserviceSelection, InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport,
	InfoBarSummarySupport, InfoBarTimeshiftState, InfoBarTeletextPlugin, InfoBarExtensions,
	InfoBarPiP, InfoBarPlugins, InfoBarSubtitleSupport, InfoBarServiceErrorPopupSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom,
	Screen):

	ALLOW_SUSPEND = True
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		if config.usage.show_infobar_lite.getValue() and config.skin.primary_skin.getValue() == "DMConcinnity-HD/skin.xml":
			self.skinName = "InfoBarLite"
		
		self["actions"] = HelpableActionMap(self, "InfobarActions",
			{
				"showMovies": (self.showMovies, _("Play recorded movies...")),
				"showRadio": (self.showRadioButton, _("Show the radio player...")),
				"showTv": (self.showTvButton, _("Show the tv player...")),
				"toogleTvRadio": (self.toogleTvRadio, _("toggels betwenn tv and radio...")),
				"openBouquetList": (self.openBouquetList, _("open bouquetlist")),
				"showMediaPlayer": (self.showMediaPlayer, _("Show the media player...")),
				"openTimerList": (self.openTimerList, _("Show the tv player...")),
				"openAutoTimerList": (self.openAutoTimerList, _("Show the tv player...")),
				"openEPGSearch": (self.openEPGSearch, _("Show the tv player...")),
				"openIMDB": (self.openIMDB, _("Show the tv player...")),
				"showMC": (self.showMediaCenter, _("Show the media center...")),
				"openSleepTimer": (self.openPowerTimerList, _("Show the Sleep Timer...")),
				'ZoomInOut': (self.ZoomInOut, _('Zoom In/Out TV...')),
				'ZoomOff': (self.ZoomOff, _('Zoom Off...')),
				'HarddiskSetup': (self.HarddiskSetup, _('Select HDD')),	
				"showWWW": (self.showPORTAL, _("Open MediaPortal...")),
				"showSetup": (self.showSetup, _("Show setup...")),
				"showFormat": (self.showFormat, _("Show Format Setup...")),
				"showPluginBrowser": (self.showPluginBrowser, _("Show the plugins...")),
				"showBoxPortal": (self.showBoxPortal, _("Show Box Portal...")),
			}, prio=2)

		self["key_red"] = Label()
		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["key_green"] = Label()

		self.allowPiP = True
		self.radioTV = 0

		for x in HelpableScreen, \
				InfoBarBase, InfoBarShowHide, \
				InfoBarNumberZap, InfoBarChannelSelection, InfoBarMenu, InfoBarEPG, InfoBarRdsDecoder, \
				InfoBarInstantRecord, InfoBarAudioSelection, InfoBarRedButton, InfoBarTimerButton, InfoBarUnhandledKey, InfoBarINFOpanel, InfoBarResolutionSelection, InfoBarVmodeButton, \
				InfoBarAdditionalInfo, InfoBarNotifications, InfoBarDish, InfoBarSubserviceSelection, InfoBarAspectSelection, \
				InfoBarTimeshift, InfoBarSeek, InfoBarCueSheetSupport, InfoBarSummarySupport, InfoBarTimeshiftState, \
				InfoBarTeletextPlugin, InfoBarExtensions, InfoBarPiP, InfoBarSubtitleSupport, InfoBarJobman, InfoBarQuickMenu, InfoBarZoom, \
				InfoBarPlugins, InfoBarServiceErrorPopupSupport:
			x.__init__(self)

		self.helpList.append((self["actions"], "InfobarActions", [("showMovies", _("Watch recordings..."))]))
		self.helpList.append((self["actions"], "InfobarActions", [("showRadio", _("Listen to the radio..."))]))

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				enigma.iPlayableService.evUpdatedEventInfo: self.__eventInfoChanged
			})

		self.current_begin_time=0
		assert InfoBar.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		InfoBar.instance = self
		self.zoomrate = 0
		self.zoomin = 1

		self.onShow.append(self.doButtonsCheck)

	def doButtonsCheck(self):
		if config.plisettings.ColouredButtons.getValue():
			self["key_yellow"].setText(_("Search"))

			if config.usage.defaultEPGType.getValue() == "Graphical EPG..." or config.usage.defaultEPGType.getValue() == "None":
				self["key_red"].setText(_("Single EPG"))
			else:
				self["key_red"].setText(_("ViX EPG"))

			if not config.plisettings.Subservice.getValue():
				self["key_green"].setText(_("Timers"))
			else:
				self["key_green"].setText(_("Subservices"))
		self["key_blue"].setText(_("Extensions"))

	def __onClose(self):
		InfoBar.instance = None

	def __eventInfoChanged(self):
		if self.execing:
			service = self.session.nav.getCurrentService()
			old_begin_time = self.current_begin_time
			info = service and service.info()
			ptr = info and info.getEvent(0)
			self.current_begin_time = ptr and ptr.getBeginTime() or 0
			if config.usage.show_infobar_on_event_change.getValue():
				if old_begin_time and old_begin_time != self.current_begin_time:
					self.doShow()

	def __checkServiceStarted(self):
		self.__serviceStarted(True)
		self.onExecBegin.remove(self.__checkServiceStarted)

	def serviceStarted(self):  #override from InfoBarShowHide
		new = self.servicelist.newServicePlayed()
		if self.execing:
			InfoBarShowHide.serviceStarted(self)
			self.current_begin_time=0
		elif not self.__checkServiceStarted in self.onShown and new:
			self.onShown.append(self.__checkServiceStarted)

	def __checkServiceStarted(self):
		self.serviceStarted()
		self.onShown.remove(self.__checkServiceStarted)

	def openBouquetList(self):
		if config.usage.tvradiobutton_mode.getValue() == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.getValue() == "ChannelList":
			self.showTvChannelList(True)
		elif config.usage.tvradiobutton_mode.getValue() == "BouquetList":
			self.showTvChannelList(True)
			self.servicelist.showFavourites()
	def showTvButton(self):
		if getBoxType().startswith('gb') or getBoxType() == 'odinm7':
			self.toogleTvRadio()
		elif getBoxType() == 'ventonhdx':
			self.showMovies()
		else:
			self.showTv()

	def showTv(self):
		if config.usage.tvradiobutton_mode.getValue() == "MovieList":
			self.showTvChannelList(True)
			self.showMovies()
		elif config.usage.tvradiobutton_mode.getValue() == "BouquetList":
			self.showTvChannelList(True)
			self.servicelist.showFavourites()
		else:
			self.showTvChannelList(True)

	def showRadioButton(self):
		if getBoxType().startswith('gb') or getBoxType() == 'ventonhdx' or getBoxType().startswith('azbox') or getBoxType() == 'odinm7':
			self.toogleTvRadio()
		else:
			self.showRadio()

	def showRadio(self):
		if config.usage.e1like_radio_mode.getValue():
			if config.usage.tvradiobutton_mode.getValue() == "BouquetList":
				self.showRadioChannelList(True)
				self.servicelist.showFavourites()
			else:
				self.showRadioChannelList(True)
		else:
			self.rds_display.hide() # in InfoBarRdsDecoder
			from Screens.ChannelSelection import ChannelSelectionRadio
			self.session.openWithCallback(self.ChannelSelectionRadioClosed, ChannelSelectionRadio, self)
	
	def toogleTvRadio(self): 
		if self.radioTV == 1:
			self.radioTV = 0
			self.showTv() 
		else: 
			self.radioTV = 1
			self.showRadio() 

	def ChannelSelectionRadioClosed(self, *arg):
		self.rds_display.show()  # in InfoBarRdsDecoder

	def showMovies(self, defaultRef=None):
		self.lastservice = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if self.lastservice and ':0:/' in self.lastservice.toString():
			self.lastservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.getValue())
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, defaultRef, timeshiftEnabled = self.timeshiftEnabled())

	def movieSelected(self, service):
		ref = self.lastservice
		del self.lastservice
		if service is None:
			if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
				self.session.nav.playService(ref)
		else:
			self.session.open(MoviePlayer, service, slist = self.servicelist, lastservice = ref)

	def showMediaPlayer(self):
		try:
			from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
			self.session.open(MediaPlayer)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPlayer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def showMediaCenter(self):
		try:
			from Plugins.Extensions.BMediaCenter.plugin import DMC_MainMenu
			self.session.open(DMC_MainMenu)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaCenter plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def openSleepTimer(self):
		from Screens.SleepTimerEdit import SleepTimerEdit
		self.session.open(SleepTimerEdit)
			
	def openTimerList(self):
		from Screens.TimerEdit import TimerEditList
		self.session.open(TimerEditList)

	def openPowerTimerList(self):
		from Screens.PowerTimerEdit import PowerTimerEditList
		self.session.open(PowerTimerEditList)

	def openAutoTimerList(self):
		try:
			for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
				if plugin.name == _("AutoTimer"):
					self.runPlugin(plugin)
					break
		except Exception, e:
			self.session.open(MessageBox, _("The AutoTimer plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def openEPGSearch(self):
		try:
			for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
				if plugin.name == _("EPGSearch") or plugin.name == _("search EPG...") or plugin.name == "Durchsuche EPG...":
					self.runPlugin(plugin)
					break
		except Exception, e:
			self.session.open(MessageBox, _("The EPGSearch plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def openIMDB(self):
		try:
			for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU ,PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
				if plugin.name == _("IMDb Details"):
					self.runPlugin(plugin)
					break
		except Exception, e:
			self.session.open(MessageBox, _("The IMDb plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def ZoomInOut(self):
		zoomval = 0
		if self.zoomrate > 3:
			self.zoomin = 0
		elif self.zoomrate < -9:
			self.zoomin = 1
		if self.zoomin == 1:
			self.zoomrate += 1
		else:
			self.zoomrate -= 1
		if self.zoomrate < 0:
			zoomval = abs(self.zoomrate) + 10
		else:
			zoomval = self.zoomrate
		print 'zoomRate:', self.zoomrate
		print 'zoomval:', zoomval
		if fileExists("/proc/stb/vmpeg/0/zoomrate"):
			file = open('/proc/stb/vmpeg/0/zoomrate', 'w')
			file.write('%d' % int(zoomval))
			file.close()

	def ZoomOff(self):
		self.zoomrate = 0
		self.zoomin = 1
		if fileExists("/proc/stb/vmpeg/0/zoomrate"):
			file = open('/proc/stb/vmpeg/0/zoomrate', 'w')
			file.write(str(0))
			file.close()

	def HarddiskSetup(self):
		from Screens.HarddiskSetup import HarddiskSelection
		self.session.open(HarddiskSelection)
		
	def showPORTAL(self):
		try:
			from Plugins.Extensions.MediaPortal.plugin import haupt_Screen
			self.session.open(haupt_Screen)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The MediaPortal plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def showSetup(self):
		from Screens.Menu import MainMenu, mdom
		root = mdom.getroot()
		for x in root.findall("menu"):
			y = x.find("id")
			if y is not None:
				id = y.get("val")
				if id and id == "setup":
					self.session.infobar = self
					self.session.open(MainMenu, x)
					return

	def showFormat(self):
		try:
			from Plugins.SystemPlugins.Videomode.plugin import videoSetupMain
			self.session.instantiateDialog(videoSetupMain)
			no_plugin = False
		except Exception, e:
			self.session.open(MessageBox, _("The VideoMode plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			
	def showPluginBrowser(self):
		from Screens.PluginBrowser import PluginBrowser
		self.session.open(PluginBrowser)
		
	def showBoxPortal(self):
		if getMachineBrand() == 'GI' or getBoxType().startswith('azbox') or getBoxType().startswith('ini') or getBoxType().startswith('venton'):
			from Screens.BoxPortal import BoxPortal
			self.session.open(BoxPortal)
		else:
			self.showMovies()

class MoviePlayer(InfoBarBase, InfoBarShowHide, \
		InfoBarMenu, InfoBarEPG, \
		InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications,
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView,
		InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, Screen, InfoBarTeletextPlugin, InfoBarAspectSelection,
		InfoBarServiceErrorPopupSupport, InfoBarExtensions, InfoBarPlugins, InfoBarPiP, InfoBarResolutionSelection, InfoBarZoom):

	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True

	instance = None

	def __init__(self, session, service, slist = None, lastservice = None):
		Screen.__init__(self, session)
		InfoBarAspectSelection.__init__(self)
		InfoBarAudioSelection.__init__(self)
		self.pts_pvrStateDialog = ""

		self["key_yellow"] = Label()
		self["key_blue"] = Label()
		self["key_green"] = Label()

		self["eventname"] = Label()
		self["state"] = Label()
		self["speed"] = Label()
		self["statusicon"] = MultiPixmap()

		self["actions"] = HelpableActionMap(self, "MoviePlayerActions",
			{
				"leavePlayer": (self.leavePlayer, _("leave movie player...")),
				"leavePlayerOnExit": (self.leavePlayerOnExit, _("leave movie player..."))
			})

		self.allowPiP = True

		for x in HelpableScreen, InfoBarShowHide, InfoBarMenu, InfoBarEPG, \
				InfoBarBase, InfoBarSeek, InfoBarShowMovies, InfoBarInstantRecord,  \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, InfoBarSubtitleSupport, \
				InfoBarTeletextPlugin, InfoBarServiceErrorPopupSupport, InfoBarExtensions, \
				InfoBarPlugins, InfoBarPiP, InfoBarZoom:
			x.__init__(self)

		self.onChangedEntry = [ ]
		self.servicelist = slist
		self.lastservice = lastservice or session.nav.getCurrentlyPlayingServiceOrGroup()
		session.nav.playService(service)
		self.cur_service = service
		self.returning = False
		self.onClose.append(self.__onClose)
		self.onShow.append(self.doButtonsCheck)

		assert MoviePlayer.instance is None, "class InfoBar is a singleton class and just one instance of this class is allowed!"
		MoviePlayer.instance = self

	def doButtonsCheck(self):
		if config.plisettings.ColouredButtons.getValue():
			self["key_yellow"].setText(_("Search"))
			self["key_green"].setText(_("Timers"))
		self["key_blue"].setText(_("Extensions"))

	def __onClose(self):
		MoviePlayer.instance = None
		from Screens.MovieSelection import playlist
		del playlist[:]
		self.session.nav.playService(self.lastservice)

	def handleLeave(self, how):
		self.is_closing = True
		if how == "ask":
			if config.usage.setup_level.index < 2: # -expert
				list = (
					(_("Yes"), "quit"),
					(_("No"), "continue")
				)
			else:
				list = (
					(_("Yes"), "quit"),
					(_("Yes, returning to movie list"), "movielist"),
					(_("Yes, and delete this movie"), "quitanddelete"),
					(_("No"), "continue"),
					(_("No, but restart from begin"), "restart")
				)

			from Screens.ChoiceBox import ChoiceBox
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)
		else:
			self.leavePlayerConfirmed([True, how])

	def leavePlayer(self):
		setResumePoint(self.session)
		self.handleLeave(config.usage.on_movie_stop.getValue())

	def leavePlayerOnExit(self):
		if self.shown:
			self.hide()
		elif self.session.pipshown and "popup" in config.usage.pip_hideOnExit.getValue():
			if config.usage.pip_hideOnExit.getValue() == "popup":
				self.session.openWithCallback(self.hidePipOnExitCallback, MessageBox, _("Disable Picture in Picture"), simple=True)
			else:
				self.hidePipOnExitCallback(True)
		elif config.usage.leave_movieplayer_onExit.getValue() == "popup":
			self.session.openWithCallback(self.leavePlayerOnExitCallback, MessageBox, _("Exit movie player?"), simple=True)
		elif config.usage.leave_movieplayer_onExit.getValue() == "without popup":	
			self.leavePlayerOnExitCallback(True)

	def leavePlayerOnExitCallback(self, answer):
		if answer:
			setResumePoint(self.session)
			self.handleLeave("quit")

	def hidePipOnExitCallback(self, answer):
		if answer:
			self.showPiP()

	def deleteConfirmed(self, answer):
		if answer:
			self.leavePlayerConfirmed((True, "quitanddeleteconfirmed"))

	def leavePlayerConfirmed(self, answer):
		answer = answer and answer[1]
		if answer is None:
			return
		if answer in ("quitanddelete", "quitanddeleteconfirmed"):
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			serviceHandler = enigma.eServiceCenter.getInstance()
			if answer == "quitanddelete":
				msg = ''
				if config.usage.movielist_trashcan.getValue():
					import Tools.Trashcan
					try:
						trash = Tools.Trashcan.createTrashFolder(ref.getPath())
						Screens.MovieSelection.moveServiceFiles(ref, trash)
						# Moved to trash, okay
						self.close()
						return
					except Exception, e:
						print "[InfoBar] Failed to move to .Trash folder:", e
						msg = _("Cannot move to trash can") + "\n" + str(e) + "\n"
				info = serviceHandler.info(ref)
				name = info and info.getName(ref) or _("this recording")
				msg += _("Do you really want to delete %s?") % name
				self.session.openWithCallback(self.deleteConfirmed, MessageBox, msg)
				return

			elif answer == "quitanddeleteconfirmed":
				offline = serviceHandler.offlineOperations(ref)
				if offline.deleteFromDisk(0):
					self.session.openWithCallback(self.close, MessageBox, _("You cannot delete this!"), MessageBox.TYPE_ERROR)
					return

		if answer in ("quit", "quitanddeleteconfirmed"):
			self.close()
		elif answer == "movielist":
			ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
			self.returning = True
			self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)
			self.session.nav.stopService()
		elif answer == "restart":
			self.doSeek(0)
			self.setSeekState(self.SEEK_STATE_PLAY)
		elif answer in ("playlist","playlistquit","loop"):
			( next_service, item , length ) = self.getPlaylistServiceInfo(self.cur_service)
			if next_service is not None:
				if config.usage.next_movie_msg.getValue():
					self.displayPlayedName(next_service, item, length)
				self.session.nav.playService(next_service)
				self.cur_service = next_service
			else:
				if answer == "playlist":
					self.leavePlayerConfirmed([True,"movielist"])
				elif answer == "loop" and length > 0:
					self.leavePlayerConfirmed([True,"loop"])
				else:
					self.leavePlayerConfirmed([True,"quit"])
		elif answer in "repeatcurrent":
			if config.usage.next_movie_msg.value:
				(item, length) = self.getPlaylistServiceInfo(self.cur_service)
				self.displayPlayedName(self.cur_service, item, length)
			self.session.nav.stopService()
			self.session.nav.playService(self.cur_service)

	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref:
			delResumePoint(ref)
		self.handleLeave(config.usage.on_movie_eof.getValue())

	def up(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveUp()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def down(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			if "keep" not in config.usage.servicelist_cursor_behavior.value:
				slist.moveDown()
			self.session.execDialog(slist)
		else:
			self.showMovies()

	def right(self):
		# XXX: gross hack, we do not really seek if changing channel in pip :-)
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapDown here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.getValue() and slist.atEnd():
							slist.nextBouquet()
						else:
							slist.moveDown()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveDown()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekFwd(self)

	def left(self):
		slist = self.servicelist
		if slist and slist.dopipzap:
			# XXX: We replicate InfoBarChannelSelection.zapUp here - we shouldn't do that
			if slist.inBouquet():
				prev = slist.getCurrentSelection()
				if prev:
					prev = prev.toString()
					while True:
						if config.usage.quickzap_bouquet_change.getValue():
							if slist.atBegin():
								slist.prevBouquet()
						slist.moveUp()
						cur = slist.getCurrentSelection()
						if not cur or (not (cur.flags & 64)) or cur.toString() == prev:
							break
			else:
				slist.moveUp()
			slist.zap(enable_pipzap = True)
		else:
			InfoBarSeek.seekBack(self)

	def showPiP(self):
		slist = self.servicelist
		if self.session.pipshown:
			if slist and slist.dopipzap:
				slist.togglePipzap()
			if self.session.pipshown:
				del self.session.pip
				self.session.pipshown = False
		else:
			from Screens.PictureInPicture import PictureInPicture
			self.session.pip = self.session.instantiateDialog(PictureInPicture)
			self.session.pip.show()
			if self.session.pip.playService(slist.getCurrentSelection()):
				self.session.pipshown = True
				self.session.pip.servicePath = slist.getCurrentServicePath()
			else:
				self.session.pipshown = False
				del self.session.pip

	def movePiP(self):
		if self.session.pipshown:
			InfoBarPiP.movePiP(self)

	def swapPiP(self):
		pass

	def showMovies(self):
		ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if ref and ':0:/' not in ref.toString():
			self.playingservice = ref # movie list may change the currently playing
		else:
			self.playingservice = enigma.eServiceReference(config.movielist.curentlyplayingservice.getValue())
		self.session.openWithCallback(self.movieSelected, Screens.MovieSelection.MovieSelection, ref)

	def movieSelected(self, service):
		if service is not None:
			self.cur_service = service
			self.is_closing = False
			self.session.nav.playService(service)
			self.returning = False
		elif self.returning:
			self.close()
		else:
			self.is_closing = False
			try:
				ref = self.playingservice
				del self.playingservice
				# no selection? Continue where we left off
				if ref and not self.session.nav.getCurrentlyPlayingServiceOrGroup():
					self.session.nav.playService(ref)
			except:
				pass		

	def getPlaylistServiceInfo(self, service):
		from MovieSelection import playlist
		for i, item in enumerate(playlist):
			if item == service:
				if config.usage.on_movie_eof.value == "repeatcurrent":
					return i+1, len(playlist)
				i += 1
				if i < len(playlist):
					return playlist[i], i+1, len(playlist)
				elif config.usage.on_movie_eof.getValue() == "loop":
					return playlist[0], 1, len(playlist)
		return None, 0, 0

	def displayPlayedName(self, ref, index, n):
		from Tools import Notifications
		Notifications.AddPopup(text = _("%s/%s: %s") % (index, n, self.ref2HumanName(ref)), type = MessageBox.TYPE_INFO, timeout = 5)

	def ref2HumanName(self, ref):
		return enigma.eServiceCenter.getInstance().info(ref).getName(ref)
