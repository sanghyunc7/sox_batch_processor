import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
info_handler = logging.FileHandler("info.log")
info_handler.setLevel(logging.INFO)
error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.ERROR)
logger.addHandler(info_handler)
logger.addHandler(error_handler)


logger.info("Hello")
logger.error("world")
logger.info(logger.getEffectiveLevel())

# info:
# Hello
# world
# 10

# error:
# world




