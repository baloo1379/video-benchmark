import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# "packages": ["os"] is used as example only
build_exe_options = {"packages": ["glob", "os", "pickle", "re", "tkinter", "datetime", "matplotlib", "numpy"]}

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="video-benchmark",
    version="0.1",
    description="CPU benchmark based on ffmpeg library",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
    include_files=["ffmpeg.exe"]
)
