[app]

# (str) Title of your application
title = El Garaje de PIPO

# (str) Package name
package.name = elgarajedepipo

# (str) Package domain (needed for android packaging)
package.domain = org.raulplaza

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 1.0

# (list) Application requirements
# IMPORTANTE: sqlite3 es vital para que la base de datos no dé error al abrir
requirements = python3,kivy,android,sqlite3,pillow

# (str) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Estos son los 3 permisos que necesita tu app para funcionar y enviar WhatsApp
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android Architecture to build for
android.archs = arm64-v8a

# (bool) allow backup
android.allow_backup = True

# (str) Icon of the application
icon.filename = %(source.dir)s/icono.png

# (bool) Enable AndroidX support. Required for many modern libraries.
android.enable_androidx = True

# (bool) Copy library instead of making a libpython.so
android.copy_libs = 1

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
