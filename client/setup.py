from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

executables = [
    Executable('test_Qt.py', 'Win32GUI')
]

setup(name='Linux PyQt test',
      version = '0.1',
      description = 'Test ability to compile PyQt app',
      options = dict(build_exe = buildOptions),
      executables = executables)
