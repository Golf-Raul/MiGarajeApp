[app]
title = Mi Garaje
package.name = migaraje
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# REQUISITOS (Fundamental para que no falle)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,android,pillow

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

# ICONO (Asegúrate de subir icono.png a GitHub)
icon.filename = %(source.dir)s/icono.png
