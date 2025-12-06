import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Set debug level for "logger_base"
logging.getLogger("logger_base").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
