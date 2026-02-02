[app]
title = Mi Garaje
package.name = migaraje
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,android,pillow
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.api = 31
android.minapi = 21
android.ndk = 25b
android.skip_update = False
icon.filename = %(source.dir)s/icono.png
