[app]
title = MarikOS Shell
package.name = marikos
package.domain = org.marik

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
