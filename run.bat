@echo off
REM Check if 'id' argument is provided
if "%~1"=="" (
  echo Please provide the 'id' argument.
  exit /b 1
)

REM Execute main.py with the 'id' argument
python main.py USA internal_USA_topic %1
