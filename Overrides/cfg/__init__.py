from .cfg import UseUI
from .cfg import WOTC
from .cfg import DryRun
# from .cfg import IncludeMods # IncludeMods is probably a bad idea
from .cfg import ExcludeMods
from .cfg import CleanOverrides
from .cfg import PromptForEach
from .cfg import IncludeOverrides, ExcludeOverrides
from .cfg import CleanActiveMods, CleanXComModOptions, CleanDefaultModOptions
from .cfg import XCOM2Dir
from .cfg import mod_paths
from .cfg import Path_VFSBase
from .cfg import FixModPaths, RemoveIniVersion, RemoveIniVersionAllFiles
from .cfg import Platform, IS_WINDOWS, IS_MACOS, IS_LINUX


__all__ = [
    'UseUI',
    'WOTC',
    'DryRun',
    # 'IncludeMods',
    'ExcludeMods',
    'CleanOverrides',
    'PromptForEach',
    'IncludeOverrides',
    'ExcludeOverrides',
    'CleanActiveMods',
    'CleanXComModOptions',
    'CleanDefaultModOptions',
    'XCOM2Dir',
    'Path_VFSBase',
    'mod_paths',
    'FixModPaths',
    'RemoveIniVersion',
    'RemoveIniVersionAllFiles',
    'Platform',
    'IS_WINDOWS',
    'IS_MACOS',
    'IS_LINUX',
]
