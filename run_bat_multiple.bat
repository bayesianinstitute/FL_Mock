@echo off

:: Define the broker service, cluster name, and internal cluster topic
set BROKER_SERVICE="test.mosquitto.org"
set CLUSTER_NAME="USA"
set INTERNAL_CLUSTER_TOPIC="internal_USA_topic"
set MIN_NODE=3

:: Define the script to run
set SCRIPT="main.py"

:: Run three instances of the script with different client IDs
for %%i in (1 2 3) do (
    start cmd /k "python %SCRIPT% %BROKER_SERVICE% %CLUSTER_NAME% %INTERNAL_CLUSTER_TOPIC%  %%i  %MIN_NODE%"
)
