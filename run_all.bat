@echo off

:: Check for admin rights
NET SESSION >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Administrator rights confirmed.
) ELSE (
    echo Please run this script as Administrator.
    goto :eof
)

:: Your existing script follows...

@REM cd FL_Mock
git pull

:: Activate virtual environment
call myenv/Scripts/activate

pip install -r requirements.txt

:: Install IPFS
@REM sudo apt update
@REM sudo apt install snapd
@REM curl -L -o kubo_v0.23.0_linux-amd64.tar.gz https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz
@REM tar -xvzf kubo_v0.23.0_linux-amd64.tar.gz
@REM cd kubo
@REM sudo bash install.sh
@REM ipfs --version
ipfs init

:: Run IPFS daemon
start cmd /k "ipfs daemon"

:: Run Django server
start cmd /k "cd FL_Mock/db && python manage.py runserver"

:: Run mlflow
start cmd /k "cd FL_Mock/core/MLOPS/Model && mlflow ui"

:: Run main program
start cmd /k "cd FL_Mock/core/MLOPS/Model && python main.py test.mosquitto.org USA %1 1"
