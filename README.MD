# NAS Kit

This is the E ink display software for the NAS Kit. It only deals with eink display with system information and fan control.
If you need OMV, install it manually.

> OMV needs to be install in a lite version of Raspberry Pi OS. If you have installed OMV on a full version of Raspberry Pi OS, you need to reinstall it.

## Installation guide

Update apt list
    
``` bash
sudo apt update
```

Install dependencies

``` bash
sudo apt install git python3.11 -y
```

Install nas kit
    
``` bash
git clone --depth=1 https://github.com/dmcooller/nas-kit.git
cd nas-kit
python3 setup.py
```

## Configuration

Optionally change `settings.ini` file to configure some application settings.

## Manual control

You can manually start/storp/restart the service with the following commands.

Start:
``` bash
sudo systemctl start nas-kit
```

Stop:
``` bash
sudo systemctl stop nas-kit
```

Restart:
``` bash
sudo systemctl restart nas-kit
```

## Install OMV 6/7

### Recommendations

I've got some nasty issues when I tried to install OMV, like loose ssh access, and not be able to log in to the web interface. 
So here are some recommendations that helped me to avoid these issues:

- Don't create user `admin` prior to installing OMV. It will cause a conflict.
- After installing OMV, you will lickly loose to connect via ssh. You can enable it in the web interface:
  1. Open `Users -> Users` page.
  2. Click on your user name.
  3. Click on `Edit` button.
  4. In `Groups` tab, check `_ssh` group.


Get Raspberry Pi IP address and remember it.

``` bash
hostname -I
```

Install OpenMediaVault

This script will install OMV 6 for `Bullseye` and OMV 7 for `Bookworm`. 

``` bash
wget -O - https://raw.githubusercontent.com/OpenMediaVault-Plugin-Developers/installScript/master/install | sudo bash
```

The device will reboot after the installation is complete.

After reboot, you can access OMV web interface with the IP address you got before.

```
http://<IP address>
```

After the web interface loaded, you will be asked to log in to be able to proceed.

The default username is `admin`, and the default password is `openmediavault`.

Done!, now you can use OMV on your Raspberry Pi.
