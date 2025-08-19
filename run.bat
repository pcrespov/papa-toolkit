@echo off
setlocal

echo Organizando imagenes y videos...
echo.

rem Set source and destination folders
set SOURCE_FOLDER=C:\Users\%USERNAME%\Dropbox\Camera Uploads
set IMAGE_DEST=C:\Users\%USERNAME%\Pictures\Organized
set VIDEO_DEST=C:\Users\%USERNAME%\Videos\Organized

echo Procesando imagenes...
python image_syncer.py "%SOURCE_FOLDER%" "%IMAGE_DEST%" -t image

echo.
echo Procesando videos...
python image_syncer.py "%SOURCE_FOLDER%" "%VIDEO_DEST%" -t video

echo.
echo Proceso completado!

rem Pause to keep the command prompt window open
pause

endlocal
