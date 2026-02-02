[app]
title = Mi Garaje
package.name = migaraje
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Hemos quitado kivymd para que la compilación sea más estable
requirements = python3,kivy==2.2.1,android,pillow

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

# Si NO tienes un archivo llamado icono.png en GitHub, 
# comenta esta línea con un # delante o fallará
icon.filename = %(source.dir)s/icono.png
