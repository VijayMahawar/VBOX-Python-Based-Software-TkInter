import cx_Freeze
import sys
import os

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

os.__file__ = r'C:\\Miniconda3\\envs\\statmath\\lib\\os.py'	
os.environ['TCL_LIBRARY'] = r'C:\Miniconda3\envs\statmath\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Miniconda3\envs\statmath\tcl\tk8.6'
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    
executables = [cx_Freeze.Executable(r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Executables_CxFreeze\vbox_app_scripts\launch_app.py',
                                    base = base, icon=r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Icon Files\favicon_transparent.ico')]

cx_Freeze.setup(name = 'VBox Processor',
               options = {'build_exe':{'packages':['tkinter', 'numpy', 'asyncio', 'appdirs', 'packaging', 'pkg_resources', 'idna', 'scipy', 'seaborn', 'folium', 'pandas', 'branca',
			                                       r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Executables_CxFreeze\ulabtools',
                                       			   r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Executables_CxFreeze\vbox_app_scripts',
                                     			   r'C:\Miniconda3\envs\statmath\site-packages\geopy', r'C:\Miniconda3\envs\statmath\site-packages\geographiclib',
												   r'C:\Miniconda3\envs\statmath\Lib\site-packages\pandastable'],
                                       'include_files':[r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Icon Files\favicon_transparent.ico',
									                    r"C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Icon Files\Vbox_Tool_Logo-removebg-removebg.png",
														os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                                        os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
														r'C:\Miniconda3\envs\statmath\site-packages\geopy', r'C:\Miniconda3\envs\statmath\site-packages\geographiclib',
												        r'C:\Miniconda3\envs\statmath\Lib\webbrowser.py', r'C:\Miniconda3\envs\statmath\Lib\site-packages\pandastable',
														r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Executables_CxFreeze\ulabtools',
                                       			        r'C:\Users\g200673\Desktop\India\Market_Support\SI_UsageCharacterization_Notebook\Vbox_GUI\Executables_CxFreeze\vbox_app_scripts']}},
               version = '1.0',
               description = 'An application for processing VBox files',
               executables = executables)