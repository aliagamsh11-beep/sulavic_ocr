[app]
title = Sulavic OCR
package.name = sulavicocr
package.domain = org.sulavic

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,tflite,ttf,otf,json,txt
source.exclude_dirs = tests,bin,.git,.github,__pycache__,build_backup,.buildozer,venv

version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,numpy,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 31
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a

android.allow_backup = True
android.accept_sdk_license = True
android.enable_androidx = True

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
