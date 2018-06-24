import os
from tkinter import *
from tkinter import filedialog, messagebox

from Overrides.constants import CFG_SECTION, CFG_FILE_NAME
from Overrides.ini_handler import XComEngineIniHandler, XComModOptionsIniHandler
from Overrides.text_processor import IniTextProcessor
from Overrides.utils import setup_logging, load_manager_config, is_xcom_path_valid


setup_logging()
manager_config = load_manager_config()

IS_WOTC = manager_config.getboolean(CFG_SECTION, "WOTC")
CLEAN_ACTIVE_MODS = manager_config.getboolean(CFG_SECTION, "CleanActiveMods")
DRY_RUN = manager_config.getboolean(CFG_SECTION, "DryRun")

XCE_FILE_NAME = "XComEngine.ini"
XCMO_FILE_NAME = "XComModOptions.ini"
DMO_FILE_NAME = "DefaultModOptions.ini"

XCOM2_CONF_PATH = XComEngineIniHandler.get_platform_specific_config_path(wotc=IS_WOTC)

XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
XCMO_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCMO_FILE_NAME


# TODO: Read these paths from XCE?
"""
[Engine.DownloadableContentEnumerator]
ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XComGame\Mods\
ModRootDirs=W:\Games\Steam\steamapps\common\XCOM 2\XCom2-WarOfTheChosen\XComGame\Mods\
ModRootDirs=W:\Games\Steam\steamapps\workshop\content\268500\
"""
Path_XCOM2Mods = manager_config[CFG_SECTION]["XCOM2Mods"]  # "W:\Games\Steam\steamapps\common\XCOM 2\XComGame\Mods"
Path_WOTCMods = manager_config[CFG_SECTION]["WOTCMods"]  # "W:\Games\Steam\steamapps\common\XCOM 2\XCom2-WarOfTheChosen\XComGame\Mods"
Path_SteamMods = manager_config[CFG_SECTION]["SteamMods"]  # "W:\Games\Steam\steamapps\workshop\content\268500"

MOD_PATHS = [
	Path_XCOM2Mods, Path_SteamMods,
	# AdditionalModsPath1, AdditionalModsPath2, AdditionalModsPath2, AdditionalModsPath3, AdditionalModsPath4
]
if IS_WOTC:
	MOD_PATHS.append(Path_WOTCMods)

print("Debug: XComEngine.ini absolute path: '%s'" % XCE_FILE_PATH)
print("Configuration: ")
print(":: WOTC: %s " % IS_WOTC)
print(":: Path_XCOM2Mods: %s " % Path_XCOM2Mods)
print(":: Path_WOTCMods: %s " % Path_WOTCMods)
print(":: Path_SteamMods: %s " % Path_SteamMods)
print(":: CleanActiveMods: %s " % CLEAN_ACTIVE_MODS)
print(":: DryRun: %s " % DRY_RUN)


class OverridesManager(object):
	xce = XComEngineIniHandler(XCE_FILE_PATH)
	xcmo = XComModOptionsIniHandler(XCMO_FILE_PATH)
	overrides_dict = {}
	found_overrides = []
	previous_overrides = []

	def __init__(self):
		self.window = Tk()
		self.xcom_path = StringVar()
		self.IsWOTC = IntVar()
		self.CleanMods = IntVar()
		self.DryRun = IntVar()

		if IS_WOTC:
			self.IsWOTC.set(1)

		if CLEAN_ACTIVE_MODS:
			self.CleanMods.set(1)

		if DRY_RUN:
			self.DryRun.set(1)

		if is_xcom_path_valid(manager_config[CFG_SECTION]["Path"]):
			self.xcom_path.set(manager_config[CFG_SECTION]["Path"])

		if is_xcom_path_valid(manager_config[CFG_SECTION]["Path"]):
			self.xcom_path.set(manager_config[CFG_SECTION]["Path"])

		lbl_path = Label(self.window, text="XCOM2 installation path:")
		lbl_path.pack()

		path_frame = Frame(self.window)
		path_entry = Entry(path_frame, textvariable=self.xcom_path, width=200)
		path_entry.pack(side=LEFT)

		browse_btn = Button(path_frame, text="Browse", command=self.changepath)
		browse_btn.pack(side=RIGHT)

		path_frame.pack()

		option_frame = Frame(self.window)
		chkWOTC = Checkbutton(option_frame, text="Process WOTC?", variable=self.IsWOTC)
		chkWOTC.pack(side=LEFT)
		chkClean = Checkbutton(option_frame, text="Clean Active Mods (If mods somehow refuse to activate/deactivate)", variable=self.CleanMods)
		chkClean.pack(side=LEFT)
		chkDry = Checkbutton(option_frame, text="Dry Run (Do nothing, see what would be changed in logs)", variable=self.DryRun)
		chkDry.pack(side=LEFT)

		option_frame.pack()

		self.btnLaunch = Button(self.window, command=self.start_clean, text="Start")
		self.btnLaunch.pack()
		self.window.resizable(width=False, height=False)
		self.window.mainloop()

	def changepath(self):
		temp_path = filedialog.askdirectory()

		if temp_path == "":
			return

		if is_xcom_path_valid(temp_path):
			self.xcom_path.set(temp_path)
		else:
			messagebox.showwarning(
						"Error",
						"Unable to find XCOM2 installation in\n(%s)" % temp_path
					)	

	def start_clean(self):
		self.btnLaunch.config(state="disabled")
		self.overrides_dict = {}
		self.found_overrides = []
		self.previous_overrides = []
		if self.init_paths():
			self.process_overrides_and_write_config()
		self.btnLaunch.config(state="normal")

	def init_paths(self):
		x_path = self.xcom_path.get()
		if is_xcom_path_valid(x_path):
			manager_config.set(CFG_SECTION, "Path", x_path)
			# Check is WOTC
			IS_WOTC = self.IsWOTC.get() and is_xcom_path_valid(os.path.join(x_path, "XCom2-WarOfTheChosen"))
			manager_config.set(CFG_SECTION, "WOTC", value='True' if IS_WOTC else 'False')
			print("Is WOTC:", IS_WOTC)

			CLEAN_ACTIVE_MODS = self.CleanMods.get() > 0
			manager_config.set(CFG_SECTION, "CleanActiveMods", value='True' if CLEAN_ACTIVE_MODS else 'False')
			print("CleanActiveMods:", CLEAN_ACTIVE_MODS)

			DRY_RUN = self.DryRun.get() > 0
			manager_config.set(CFG_SECTION, "DryRun", value='True' if DRY_RUN else 'False')
			print("DryRun:", DRY_RUN)

			MOD_PATHS = []
			temp_path = os.path.abspath(os.path.join(x_path, "XComGame/Mods"))
			if os.path.exists(temp_path):
				Path_XCOM2Mods = temp_path
				MOD_PATHS.append(Path_XCOM2Mods)
				manager_config.set(CFG_SECTION, "XCOM2Mods", Path_XCOM2Mods)
			temp_path = os.path.abspath(os.path.join(x_path, "../../workshop/content/268500"))
			if os.path.exists(temp_path):
				Path_SteamMods = temp_path
				MOD_PATHS.append(Path_SteamMods)
				manager_config.set(CFG_SECTION, "SteamMods", Path_SteamMods)
			if IS_WOTC:
				temp_path = os.path.abspath(os.path.join(x_path, "XCom2-WarOfTheChosen/XComGame/Mods"))
				if os.path.exists(temp_path):
					Path_WOTCMods = temp_path
					MOD_PATHS.append(Path_WOTCMods)
				manager_config.set(CFG_SECTION, "WOTCMods", Path_WOTCMods)
			
			fp = open(CFG_FILE_NAME, 'w')
			manager_config.write(fp)
			fp.close()

			XCOM2_CONF_PATH = XComEngineIniHandler.get_platform_specific_config_path(wotc=IS_WOTC)

			XCE_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCE_FILE_NAME
			XCMO_FILE_PATH = os.path.expanduser('~') + XCOM2_CONF_PATH + XCMO_FILE_NAME

			self.xce = XComEngineIniHandler(XCE_FILE_PATH)
			self.xcmo = XComModOptionsIniHandler(XCMO_FILE_PATH)
			self.dcmo = XComModOptionsIniHandler(os.path.join(x_path, ("XCom2-WarOfTheChosen/XComGame/Config/"
												if IS_WOTC else "XComGame/Config/") + DMO_FILE_NAME))

			self._find_overrides_in_mods_paths()
			self._check_for_duplicate_overrides()
			print("Found and Parsed ModClassOverrides: %s" % len(self.found_overrides))
			self._get_existing_overrides()
			return True
		else:
			messagebox.showwarning("Error", "Invalid XCOM2 installation path")
			return False

	@classmethod
	def find_inis_in_mods_path(cls, mods_path):
		engine_ini_paths = []
		if not mods_path:
			return []
		for root, dirs, files in os.walk(mods_path):
			for file_name in files:
				if file_name == "XComEngine.ini":
					file_path = os.path.join(root, file_name)
					engine_ini_paths.append(file_path)

		print("%s 'XComEngine.ini' files found in mods path: '%s'" % (len(engine_ini_paths), mods_path))
		for p in engine_ini_paths:
			print("Path: %s" % p)
		return engine_ini_paths

	def _get_existing_overrides(self):
		print(
			"Retrieving existing overrides from 'XComEngine.ini' in user config folder ('%s') for comparison."
			% XCE_FILE_PATH
		)
		self.previous_overrides = self.xce.get_overrides_from_file(self.xce.file_path)
		print("Previous Overrides in XComEngine.ini: %s" % len(self.previous_overrides))

	def _find_overrides_in_mods_paths(self):
		# Get file paths to all XComEngine.ini files in known mod paths (XCOM2, WotC, Steam, + Additionals)
		for mod_path in MOD_PATHS:
			for ini_path in self.find_inis_in_mods_path(mod_path):

				# Get ModClassOverride lines in found files
				overs = XComEngineIniHandler.get_overrides_from_file(ini_path)
				for found_override in overs:
					source_mod_name = found_override.source_mod_name
					if source_mod_name is not None and source_mod_name in self.xcmo.active_mods:
						self.found_overrides.append(found_override)
					else:
						print("Ignoring override from inactive Mod: %s" % source_mod_name)

	def _check_for_duplicate_overrides(self):
		# Parse the ModClassOverride lines so we can warn about duplicates
		for override in self.found_overrides:
			if override.base_class in self.overrides_dict:
				existing = self.overrides_dict[override.base_class]
				if override.mod_class == existing.mod_class:
					print(
						"\n\nWARNING: Duplicate ModClassOverride lines found! "
						"Possible mod conflict or maybe just a typo in one mod if both source files are the same.\n"
						"Lines:\n"
						"1: '%s' - Source File: '%s'\n"
						"2: '%s' - Source File: '%s'\n" % (
						existing, existing.source_file, override, override.source_file)
					)
				else:
					print(
						"\n\nWARNING: Multiple ModClassOverrides for the same BaseGameClass with different ModClasses! "
						"Probable mod conflict!\n"
						"Lines:\n"
						"1: '%s' - Source File: '%s'\n"
						"2: '%s' - Source File: '%s'\n" % (
						existing, existing.source_file, override, override.source_file)
					)
			self.overrides_dict[override.base_class] = override
		# TODO: Halt on duplicates?

	def _determine_overrides_to_add(self):
		new_overrides = self.found_overrides.copy()
		if self.previous_overrides:
			new_overrides = list(set(self.found_overrides) - set(self.previous_overrides))
		return new_overrides

	def _determine_overrides_to_remove(self):
		removed_overrides = []
		if self.previous_overrides:
			removed_overrides = list(set(self.previous_overrides) - set(self.found_overrides))
		return removed_overrides

	def _determine_if_changes_needed(self):
		change_needed = False
		new_overrides = self._determine_overrides_to_add()
		for new_override in new_overrides:
			print("Will add: %s - Source File: %s" % (new_override, new_override.source_file))

		removed_overrides = self._determine_overrides_to_remove()
		for removed_override in removed_overrides:
			print("Will remove: %s - Source File: %s" % (removed_override, removed_override.source_file))

		if new_overrides or removed_overrides:
			change_needed = True

		return change_needed

	def process_overrides_and_write_config(self):
		if self._determine_if_changes_needed():
			print("==== Changes needed - Proceeding")

			print("== Updating overrides in 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
			text = self.xce.get_text()
			if self.found_overrides:
				clean_text = IniTextProcessor.replace_old_overrides(text, self.found_overrides)
			else:
				# No new overrides to add, just clean up instead
				clean_text = IniTextProcessor.clean_out_all_overrides(text)

			print("== Doing cleanup of 'XComEngine.ini' in user config folder ('%s')" % XCE_FILE_PATH)
			clean_text = IniTextProcessor.repair_config_text(clean_text)

			self.xce.write_text(clean_text, dry_run=DRY_RUN)

		else:
			print("==== No Changes needed - Not modifying XComEngine.ini!")

		print("== Doing cleanup of 'XComModOptions.ini' in user config folder ('%s')" % XCE_FILE_PATH)
		self.xcmo.repair_active_mods(dry_run=DRY_RUN, clean_mods=CLEAN_ACTIVE_MODS)
		self.dcmo.repair_default_mods(dry_run=DRY_RUN, clean_mods=CLEAN_ACTIVE_MODS)

		messagebox.showinfo(
			"Finished!", "Open XCOM2OM.log in a text editor to see detailed results of what was done.\n"
		)


if __name__ == "__main__":
	manager = OverridesManager()
	#manager.process_overrides_and_write_config()
