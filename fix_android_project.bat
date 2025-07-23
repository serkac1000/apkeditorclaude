@echo off
echo Fixing Android project configuration...

set PROJECT_DIR=C:\Users\HOT\Downloads\MyAwesomeApp_004

REM Create directories if they don't exist
mkdir "%PROJECT_DIR%\MyAwesomeApp\app\src\main" 2>nul

REM Copy gradle.properties to root and module level
copy /Y "gradle.properties" "%PROJECT_DIR%\gradle.properties"
copy /Y "gradle.properties" "%PROJECT_DIR%\MyAwesomeApp\gradle.properties"

REM Copy AndroidManifest.xml to the correct location
copy /Y "AndroidManifest.xml" "%PROJECT_DIR%\MyAwesomeApp\app\src\main\AndroidManifest.xml"

echo Done! Files have been copied to the correct locations.
echo.
echo Root gradle.properties: %PROJECT_DIR%\gradle.properties
echo Module gradle.properties: %PROJECT_DIR%\MyAwesomeApp\gradle.properties
echo AndroidManifest.xml: %PROJECT_DIR%\MyAwesomeApp\app\src\main\AndroidManifest.xml
echo.
pause