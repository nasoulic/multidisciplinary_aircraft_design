@echo off
set "directory=results"

REM Check if the directory exists
if not exist "%directory%" (
    echo Directory does not exist.
    exit /b
)

REM Delete all files in the directory
del /q "%directory%\*" > nul

REM Delete all subdirectories and their contents
for /d %%i in ("%directory%\*") do (
    rd /s /q "%%i" > nul
)

echo All internal files and directories in %directory% have been removed.
