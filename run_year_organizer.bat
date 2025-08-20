@echo off
setlocal

echo Organizando carpetas por año...
echo.

rem Set target folder - change this path as needed
set TARGET_FOLDER=C:\Users\%USERNAME%\Pictures\Organized

echo Organizando carpetas con formato YYYY-MM-DD en carpetas por año...
python year_organizer.py "%TARGET_FOLDER%"

echo.
echo Proceso completado!

rem Pause to keep the command prompt window open
pause

endlocal