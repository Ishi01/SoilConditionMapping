@echo off
REM Define the Miniconda installation path
set CONDA_PATH=%USERPROFILE%\Miniconda3

REM Step 1: Check if Miniconda is installed, if not, install it
if not exist "%CONDA_PATH%" (
    echo Miniconda not found. Installing Miniconda...
    REM Run the Miniconda installer (assuming the installer is included in the same folder)
    start /wait "" "Miniconda3-latest-Windows-x86_64.exe" /InstallationType=JustMe /AddToPath=0 /S /D=%CONDA_PATH%
    call "%CONDA_PATH%\Scripts\conda.bat" init
) else (
    echo Miniconda already installed.
)

REM Step 2: Add Miniconda to PATH for the current session
set "PATH=%CONDA_PATH%\Scripts;%CONDA_PATH%\condabin;%PATH%"

REM Step 3: Activate the base conda environment and update conda
call conda.bat activate
call conda.bat update conda -y

REM Step 4: Create the project conda environment if it does not exist
set CONDA_ENV_NAME=pg
call conda env list | findstr /i %CONDA_ENV_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo Creating Conda environment named %CONDA_ENV_NAME%...
    call conda env create --file environment.yml
) else (
    echo Conda environment named %CONDA_ENV_NAME% already exists.
)

REM Step 5: Activate the Conda environment
call conda activate %CONDA_ENV_NAME%

REM Step 6: Run the main Python script
echo Running main.py...
python main.py

pause