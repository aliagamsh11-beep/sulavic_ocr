[app]
title = Sulavic OCR
package.name = sulavicocr
package.domain = org.sulavic

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,otf
source.exclude_dirs = tests,bin,.git,.github,__pycache__,build_backup,.buildozer,venv,models

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

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
