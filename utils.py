from config import HOST_NAME

from subprocess import run, PIPE, DEVNULL

import cv2
import numpy as np

# HOST_NAME = "127.0.0.1:5625"

run(f"adb connect {HOST_NAME}", stdout=DEVNULL)

def get_screenshot() -> np.ndarray:
    raw_screen = run(
        f"adb -s {HOST_NAME} exec-out screencap -p", stdout=PIPE).stdout
    return cv2.imdecode(np.frombuffer(raw_screen, np.uint8), cv2.IMREAD_COLOR)

def tap(x: int, y: int):
    run(f"adb -s {HOST_NAME} shell input tap {x} {y}")

def swipe(x: int, y: int, dx: int = 0, dy: int = 0, t: int = 100):
    run(f"adb -s {HOST_NAME} shell input swipe {x} {y} {x + dx} {y + dy} {t}")

def start():
    run(f"adb -s {HOST_NAME} shell su -c am start com.EnglishCool.Vocab/com.unity3d.player.UnityPlayerActivity")

def stop():
    run(f"adb -s {HOST_NAME} shell su -c am force-stop com.EnglishCool.Vocab")

def get_data():
    run(f"adb -s {HOST_NAME} pull /storage/emulated/0/Android/data/com.EnglishCool.Vocab/files/wordcool_user.db")

def update_data():
    run(f"adb -s {HOST_NAME} push wordcool_user.db /sdcard/Download/")
    run(f"adb -s {HOST_NAME} shell su -c mv /sdcard/Download/wordcool_user.db /storage/emulated/0/Android/data/com.EnglishCool.Vocab/files/wordcool_user.db")

def get_f_data():
    run(f"adb -s {HOST_NAME} shell su -c cp /data/data/com.EnglishCool.Vocab/shared_prefs/com.EnglishCool.Vocab.v2.playerprefs.xml /sdcard/Download/com.EnglishCool.Vocab.v2.playerprefs.xml")
    run(f"adb -s {HOST_NAME} pull /sdcard/Download/com.EnglishCool.Vocab.v2.playerprefs.xml")
    run(f"adb -s {HOST_NAME} shell su -c rm /sdcard/Download/com.EnglishCool.Vocab.v2.playerprefs.xml")

def update_f_data():
    run(f"adb -s {HOST_NAME} push com.EnglishCool.Vocab.v2.playerprefs.xml /sdcard/Download/")
    run(f"adb -s {HOST_NAME} shell \"su -c 'cat /sdcard/Download/com.EnglishCool.Vocab.v2.playerprefs.xml > /data/data/com.EnglishCool.Vocab/shared_prefs/com.EnglishCool.Vocab.v2.playerprefs.xml'\"")
    run(f"adb -s {HOST_NAME} shell su -c rm /sdcard/Download/com.EnglishCool.Vocab.v2.playerprefs.xml")
