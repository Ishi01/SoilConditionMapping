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

REM Step 3: Activate the base conda environment to run commands
call conda.bat activate base

REM Step 4: Create the project conda environment if it does not exist
set CONDA_ENV_NAME=pg
call conda env list | findstr /i %CONDA_ENV_NAME% >nul
if %ERRORLEVEL% NEQ 0 (
    echo Creating Conda environment named %CONDA_ENV_NAME%...
    call conda.bat env create --file environment.yml
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create Conda environment. Exiting...
        pause
        exit /b
    )
) else (
    echo Conda environment named %CONDA_ENV_NAME% already exists.
)

REM Step 5: Create a temporary script to activate the environment and run the Python script
echo Activating Conda environment and running the main Python script...

REM Create a temporary batch script for running the Python code within the conda environment
set TEMP_SCRIPT="%TEMP%\run_pg_env.bat"
echo @echo off > %TEMP_SCRIPT%
echo call conda.bat activate %CONDA_ENV_NAME% >> %TEMP_SCRIPT%
echo python main.py >> %TEMP_SCRIPT%
echo exit >> %TEMP_SCRIPT%

REM Step 6: Run the temporary script
call %TEMP_SCRIPT%

REM Clean up
del %TEMP_SCRIPT%

pause
