import configparser
import logging


logger = logging.getLogger(__name__)


class AppSettings:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.fan_min: int = 25
        self.fan_max: int = 100
        self.temp_ok: int = 50
        self.screen_time_out: int = 60 # in seconds
        self._load_and_validate()

    def _load_and_validate(self):
        config = configparser.ConfigParser()
        config.read(self.file_path)

        self.fan_min = config.getint('Settings', 'fan_min', fallback=self.fan_min)
        self.fan_max = config.getint('Settings', 'fan_max', fallback=self.fan_max)
        self.temp_ok = config.getint('Settings', 'temp_ok', fallback=self.temp_ok)
        self.screen_time_out = config.getint('Settings', 'screen_time_out', fallback=self.screen_time_out)

        # Validate FAN_MIN and FAN_MAX
        if not (0 <= self.fan_min <= 100):
            self.fan_min = 25
            logger.warning("FAN_MIN must be between 0 and 100. Using default value.")
        if not (0 <= self.fan_max <= 100):
            self.fan_max = 100
            logger.warning("FAN_MAX must be between 0 and 100. Using default value.")
        if self.fan_min > self.fan_max:
            self.fan_min = 25
            self.fan_max = 100
            logger.warning("FAN_MIN cannot be higher than FAN_MAX. Using default values.")

    def _param_exists(self, param: str) -> bool:
        config = configparser.ConfigParser()
        config.read(self.file_path)
        return param in config['Settings']

    def save_param(self, param: str, value):
        if not self._param_exists(param):
            raise ValueError(f"Parameter {param} does not exist in settings file.")
        
        config = configparser.ConfigParser()
        config.read(self.file_path)
        config['Settings'][param] = str(value)
        with open(self.file_path, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    def __str__(self):
        return f"Settings(fan_min={self.fan_min}, fan_max={self.fan_max}, temp_ok={self.temp_ok}, screen_time_out={self.screen_time_out})"

try:
    settings = AppSettings('settings.ini')
    logger.info("Settings loaded: %s", settings)
except Exception as e:
    logger.error("Error loading settings: %s", e)
