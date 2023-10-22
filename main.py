import minecraft_launcher_lib
import subprocess

version = input('Enter Minecraft version: ')
username = input('Enter Username: ')

minecraft_launcher_lib.install.install_minecraft_version(versionid=version, minecraft_directory=minecraft_launcher_lib.utils.get_minecraft_directory())

options = {
    'username': username,
    'uuid': '',
    'token': ''
    }

subprocess.call(minecraft_launcher_lib.command.get_minecraft_command(version=version, minecraft_directory=minecraft_launcher_lib.utils.get_minecraft_directory(), options=options))
