[app]
title = Examen ANRE
package.name = examenanre
package.domain = ro.examen

source.dir = .
source.include_exts = py,png,json

version = 1.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
