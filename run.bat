@echo off
REM Check if 'id' argument is provided
if "%~1"=="" (
  echo Please provide the 'id' argument.
  exit /b 1
)

REM Execute main.py with the 'id' argument and add '5' at the end
python main.py test.mosquitto.org USA  %1 1