@echo off
REM Hardcoded MQTT broker
set MQTT_BROKER="test.mosquitto.org"

REM Check if the correct number of arguments is provided
if "%~2"=="" (
    echo Usage: %0 ^<TRAINING_NAME^> ^<ROLE^>
    exit /B 1
)

REM Run the Python script with the provided parameters
python.exe main.py %MQTT_BROKER% %1 %2
