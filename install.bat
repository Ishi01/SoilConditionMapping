@echo off
setlocal enabledelayedexpansion

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"

REM Define the Miniconda installation path
set "CONDA_PATH=%USERPROFILE%\miniconda3"

REM Check if Miniconda is installed
if not exist "%CONDA_PATH%" (
    echo Miniconda not found. Installing Miniconda...

    REM Check if the Miniconda installer exists
    if not exist "%SCRIPT_DIR%Miniconda3-latest-Windows-x86_64.exe" (
        echo Miniconda installer not found in the script directory.
        echo Please download Miniconda3-latest-Windows-x86_64.exe and place it in the same directory as this script.
        pause
        exit /b 1
    )

    REM Run the Miniconda installer
    start /wait "" "%SCRIPT_DIR%Miniconda3-latest-Windows-x86_64.exe" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%CONDA_PATH%

    echo Miniconda installed successfully.
) else (
    echo Miniconda found at %CONDA_PATH%
)

REM Add Miniconda to PATH for this session
set "PATH=%CONDA_PATH%;%CONDA_PATH%\Scripts;%CONDA_PATH%\Library\bin;%PATH%"

REM Check if environment.yml exists
if not exist "%SCRIPT_DIR%environment.yml" (
    echo environment.yml not found in the script directory.
    echo Please ensure environment.yml is in the same directory as this script.
    pause
    exit /b 1
)

REM Create the conda environment
set "ENV_NAME=pg"
call conda env create -f "%SCRIPT_DIR%environment.yml"

echo Environment setup complete.
echo To activate the environment, use: conda activate %ENV_NAME%
echo Or if you want to initiate the program, run SoilMapping.exe

pause
