git clone https://github.com/xxchaosxx210/fake-location.git
mv -f ./fake-location/*.* ./
rm -rf ./fake-location
echo Compiling APK...
buildozer -v android debug
echo Removing previous APK...
adb uninstall org.fakelocation.fakelocation
echo Installing APK to device...
adb install ./bin/*.apk
echo Cearing logs
adb logcat -c
echo Launching APK...
adb shell monkey -p org.fakelocation.fakelocation -c android.intent.category.LAUNCHER 1
echo Running logger
adb logcat "python:I" "*:S"

