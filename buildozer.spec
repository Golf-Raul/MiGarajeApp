[app]
title = El Garaje de PIPO
package.name = elgarajedepipo
package.domain = org.raulplaza
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.2.1,android,sqlite3,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.enable_androidx = True
icon.filename = %(source.dir)s/icono.png

[buildozer]
log_level = 2
warn_on_root = 1
