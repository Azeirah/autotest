import settings
import subprocess
import sys
import os
import fileinput


def configure_php_ini(protrace=False, debugger=False):
    load_plugin = protrace or debugger
    with fileinput.FileInput(settings.php_ini_location, inplace=True, backup='.bak') as f:
        for line in f:
            if 'xdebug.auto_trace' in line:
                if protrace:
                    print(line.replace('; ', '').replace(';', ''), end='')
                else:
                    print('; ' + line, end='')
            elif 'xdebug.profiler_enable' in line:
                if protrace:
                    print(line.replace('; ', '').replace(';', ''), end='')
                else:
                    print('; ' + line, end='')
            elif 'xdebug.remote_enable' in line:
                if debugger:
                    print(line.replace('; ', '').replace(';', ''), end='')
                else:
                    print('; ' + line, end='')
            elif 'php_xdebug' in line and 'zend_extension' in line:
                if load_plugin:
                    print(line.replace('; ', '').replace(';', ''), end='')
                else:
                    print('; ' + line, end='')
            else:
                print(line, end='')


def restart_apache():
    print(settings.apache_stop_command)
    subprocess.call(settings.apache_stop_command)
    print(settings.apache_start_command)
    subprocess.call(settings.apache_start_command)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("ctl.py <protrace> <debug>")
        sys.exit()
    configure_php_ini(bool(int(sys.argv[1])), bool(int(sys.argv[2])))
    restart_apache()