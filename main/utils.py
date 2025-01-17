import logging
import subprocess
import os
import RPi.GPIO as GPIO
import time

from settings import settings


logger = logging.getLogger(__name__)

FAN_PWM = 18
LED_PWM = 26
fan_pwm_freq = 100
led_pwm_freq = 1

FAN_MAX = settings.fan_max
FAN_MIN = settings.fan_min
fan_power = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
output_list = [FAN_PWM,LED_PWM]
GPIO.setup(output_list, GPIO.OUT)

fan_pwm_pin = GPIO.PWM(FAN_PWM, fan_pwm_freq)
led_pwm_pin = GPIO.PWM(LED_PWM, led_pwm_freq)
fan_pwm_pin.start(0)
led_pwm_pin.start(0) # Turn off LED


class PID():
    def __init__(self, P=1, I=1, D=1, expect=0):
        self.P = float(P)
        self.I = float(I)
        self.D = float(D)
        self.expect = expect
        self.error = 0
        self.last_error = 0
        self.error_sum = 0

    @property
    def pval(self):
        return self.error

    @property
    def ival(self):
        self.error_sum += self.error
        return self.error_sum

    @property
    def dval(self):
        return self.error - self.last_error

    def run(self, value, mode="PID"):
        self.last_error = self.error
        self.error = value - self.expect
        logging.debug("Error: %s, Last Error: %s, Pval: %s, P: %s", self.error, self.last_error, self.pval, self.P)
        result_p = self.P * self.pval
        result_i = self.I * self.ival
        result_d = self.D * self.dval
        mode = mode.upper()
        result = 0.0
        if "P" in mode:
            result += result_p
        if "I" in mode:
            result += result_i
        if "D" in mode:
            result += result_d
        return result

#run_command linux
def run_command(cmd=""):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    logging.debug("Command: %s\nStatus: %s\nResult: %s", cmd, status, result)
    return status, result

def cpu_temperature():          # cpu_temperature
    raw_cpu_temperature = subprocess.getoutput("cat /sys/class/thermal/thermal_zone0/temp") 
    cpu_temperature = round(float(raw_cpu_temperature)/1000,1)               # convert unit
    cpu_temperature = str(cpu_temperature)
    return cpu_temperature

def gpu_temperature():          # gpu_temperature(
    raw_gpu_temperature = subprocess.getoutput( 'vcgencmd measure_temp' )
    gpu_temperature = round(float(raw_gpu_temperature.replace( 'temp=', '' ).replace( '\'C', '' )), 1)
    gpu_temperature = str(gpu_temperature)
    return gpu_temperature

def cpu_usage():                # cpu_usage
    # result = str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print($2)}'").readline().strip())
    result = os.popen("mpstat").read().strip()
    result = result.split('\n')[-1].split(' ')[-1]
    result = round(100 - float(result), 2)
    result = str(result)
    logging.debug("CPU Usage: %s", result)
    return result

def disk_space():               # disk_space
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()         
        if i==2:
            return line.split()[1:5]

def portable_hard_disk_info():
    disk_num = os.popen("df -h | grep '/dev/sd' -c")
    phd = os.popen("df -h | grep '/dev/sd'")
    i = 0
    phd_line = disk_num.readline()

    line_list = []
    if int(phd_line) != 0:
        while 1:
            i = i +1
            line = phd.readline()
            line_list.append(line.split()[0:6])
            if i==int(phd_line):
                return line_list
    else:
        return []

def ram_info():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return list(map(lambda x:round(int(x) / 1000,1), line.split()[1:4]))

def pi_read():
    result = {
        "cpu_temperature": cpu_temperature(), 
        "gpu_temperature": gpu_temperature(),
        "cpu_usage": cpu_usage(), 
        "disk": disk_space(), 
        "ram": ram_info(), 
        # "battery": power_read(),
    }
    return result

def temperature_read():
    result = {
        "cpu_temperature": cpu_temperature(), 
        "gpu_temperature": gpu_temperature(),
    }
    return result

def top_process(n: int)->list:
    """
    Get top N processes with highest CPU usage

    Return example:
    [
        ['python3', '1.0', '22.5'],
        ['systemd', '0.1', '10.5']
    ]
    """
    command = (
        "ps -eo comm,%cpu,rss --sort=-%cpu | "
        "grep -v '^ps ' | "  # Exclude 'ps'
        "awk 'NR==1 {print $1, $2, \"RSS(MB)\"} NR>1 {printf \"%s %s %.1f\\n\", $1, $2, $3/1024}' | "
        "head -n " + str(n+1)
    )
    top = os.popen(command).read()    # extract service name, CPU%, MEM% to list
    result = top.split('\n')[1:-1]
    result = list(map(lambda x: x.split(), result))
    return result


# def fan_control(temp = 0):
#     if temp >=68:
#         fan_duty_cycle = round(float(temp-67)*30,1)
#         led_freq = int(temp-67)
#         if  fan_duty_cycle >= 100:
#             fan_duty_cycle = 100
        
#         fan_pwm_pin.ChangeDutyCycle(fan_duty_cycle)
#         led_pwm_pin.ChangeDutyCycle(100)  
        
#     else:
#         fan_pwm_pin.ChangeDutyCycle(0)
#         led_pwm_pin.ChangeDutyCycle(0) 

def fan_power_read():
    global fan_power
    return round(fan_power,1)



def getIP(ifaces=['wlan0', 'eth0', 'end0']):
    import re
    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = 'ip addr show {}'.format(iface)
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?=\/)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return False

def pid_control():
    global fan_power

    temp_ok = settings.temp_ok
    # Turn on/off fan if temperature is lower/higher for `n` times counter
    temp_times_counter_max = 5

    pid = PID(
        P = 0.5,
        I = 1,
        D = 1,
        expect = temp_ok,
    )
    dc = FAN_MAX
    temp_ok_times = 0
    temp_high_times = 0
    while True:
        try:
            temp = (float(cpu_temperature())+float(gpu_temperature()))/2.0
        except OSError as err:
            logger.error("Error reading temperature: %s", err)
            # Consider temperature as high if reading fails
            temp = temp_ok + 10

        # Increase counters depending on temperature
        if temp < temp_ok:
            temp_ok_times += 1
            temp_high_times = 0
        else:
            temp_ok_times = 0
            temp_high_times += 1

        # Turn off fan if temperature is lower than temp_ok for `temp_ok_times` times
        if temp_times_counter_max < temp_ok_times:
            dc = 0
        # Turn on fan if temperature is higher than temp_ok for `temp_high_times` times
        elif temp_times_counter_max < temp_high_times:
            dc += pid.run(temp, mode="PD")
            dc = min(FAN_MAX, max(FAN_MIN, dc))
        fan_power = dc
        logging.debug("Temp: %s, DC: %s", temp, dc)
        fan_pwm_pin.ChangeDutyCycle(dc)
        #led_pwm_pin.ChangeDutyCycle(dc) # Turn off LED
        time.sleep(5)

# if __name__ == '__main__':
#     logging.debug("Portale Hard Disk Info: %s", portable_hard_disk_info())
