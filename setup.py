import subprocess


def run_command(cmd=""):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result

def do(msg="", cmd=""):
    print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='')
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
        return result
    print('Error')
    raise OSError("%s command:\n %s error:\n  Status:%s\n  Error:%s" % (cmd, msg, status, result))


def install():
    try:
        do(msg="Enable SPI",
            cmd='run_command("sudo raspi-config nonint do_spi 0")')
        ### Rpi_epd_lib
        do(msg="wget BCM2835",
            cmd='run_command("wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.75.tar.gz")')
        do(msg="tar and make install BCM2835",
            cmd='run_command("tar zxvf bcm2835-1.75.tar.gz && cd bcm2835-1.75/ && sudo ./configure && sudo make && sudo make check && sudo make install")')
        # do(msg="install wiringpi",
        #     cmd='run_command("sudo apt-get install wiringpi && cd /tmp && wget https://project-downloads.drogon.net/wiringpi-latest.deb && sudo dpkg -i wiringpi-latest.deb")')
        do(msg="apt-get update",
            cmd='run_command("sudo apt-get update")')
        do(msg="apt-get install python3-pip",
            cmd='run_command("sudo apt-get install python3-pip python3-venv -y")')
        do(msg="apt-get install sysstat",
            cmd='run_command("sudo apt-get install sysstat -y")')
        do(msg="create Python virtual environment",
            cmd='run_command("python3 -m venv venv")')
        do(msg="install Python requirements",
            cmd='run_command("./venv/bin/pip install -r requirements.txt")')

        base_path = do(msg="Get base path",
            cmd='run_command("pwd")').rstrip()
        do(msg="cp ./bin/nas-kit /usr/bin/nas-ki",
            cmd='run_command("sudo cp ./bin/nas-kit /usr/bin/nas-kit")')
        do(msg="Set base path to the app",
            cmd='run_command("sudo sed -i \'s|%s|%s|g\' /usr/bin/nas-kit")' % ('{base_path}', base_path))
        do(msg="cp ./bin/nas-kit.service /lib/systemd/system/nas-kit.service",
            cmd='run_command("sudo cp ./bin/nas-kit.service /lib/systemd/system/nas-kit.service")')
        do(msg="chmod +x /usr/bin/nas-kit",
            cmd='run_command("sudo chmod +x /usr/bin/nas-kit")')
        do(msg="systemctl daemon-reload",
            cmd='run_command("sudo systemctl daemon-reload")')
        do(msg="systemctl enable nas-kit.service",
            cmd='run_command("sudo systemctl enable nas-kit.service")')
        do(msg="systemctl start nas-kit",
            cmd='run_command("sudo systemctl start nas-kit")')


    ### install epd_code
        # do(msg="install nas-kit",
        #     cmd='run_command("cd ~")')

    ### Setup OMV env and install OMV
        # do(msg="Enter-file",
        #     cmd='run_command("cd ~/nas-kit/file")') 
        # do(msg="Nas-Source",
        #     cmd='run_command("sudo chmod 777 source-code && sudo ./source-code")')
        # do(msg="Nas-deb-setup",
        #     cmd='run_command("sudo chmod 777 nas-build && sudo ./nas-build")')
        # do(msg="install openmediavault",
        #     cmd='run_command("sudo apt-get install openmediavault-keyring openmediavault -y")') 
        # do(msg="Populate the database",
        #     cmd='run_command("sudo omv-confdbadm populate")')
    except OSError as e:
        print("\n\nError happened in install process:")
        print(e)

    print("Finished")

if __name__ =="__main__":
    install()