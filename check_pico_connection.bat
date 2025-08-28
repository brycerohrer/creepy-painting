@echo off
echo ================================================
echo Raspberry Pi Pico Connection Checker
echo ================================================
echo.

echo Checking for Pico devices...
echo.

REM Check for Pico in device manager
echo [1/3] Checking Device Manager for Pico...
powershell "Get-PnpDevice | Where-Object {$_.FriendlyName -like '*Pico*' -or $_.FriendlyName -like '*Raspberry*'} | Format-Table -AutoSize"

echo.
echo [2/3] Checking COM Ports...
powershell "Get-PnpDevice | Where-Object {$_.Class -eq 'Ports'} | Format-Table -AutoSize"

echo.
echo [3/3] Checking USB devices...
powershell "Get-PnpDevice | Where-Object {$_.Class -eq 'USB'} | Where-Object {$_.FriendlyName -like '*Pico*' -or $_.FriendlyName -like '*Raspberry*'} | Format-Table -AutoSize"

echo.
echo ================================================
echo Quick Commands:
echo ================================================
echo.
echo To see all USB devices:
echo   powershell "Get-PnpDevice | Where-Object {$_.Class -eq 'USB'}"
echo.
echo To see all COM ports:
echo   mode
echo.
echo To test a specific COM port (replace COM3):
echo   mode COM3
echo.
echo ================================================
echo.

REM Check if Python script exists and run it
if exist "check_pico_connection.py" (
    echo Running Python detection script...
    python check_pico_connection.py
) else (
    echo Python script not found. Running basic detection only.
)

echo.
pause 