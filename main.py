from src.core.config import ConfigManager
from src.core.logger import LoggerManager

print("===================================")
print("      ICT MNQ Trading Bot V1")
print("===================================")

config = ConfigManager()
config.load()

logger = LoggerManager()

logger.info("Bot Started Successfully")

config.show()

logger.info("Configuration Loaded")

print("Bot is Ready.")