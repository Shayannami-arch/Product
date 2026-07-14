[app]

title = ProductApp
package.name = productappfinal2
package.domain = org.productapp

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt,dat,db,sqlite,ttf

version = 1.2

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename =

# IMPORTANT: Do not leave this empty.
# Empty value generated invalid permission: android.permission.
android.permissions = INTERNET

android.api = 35
android.minapi = 24
android.ndk = 28c
android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 0
