import logging
from devgoldyutils import add_custom_handler, Colours

__all__ = ("osaker_logger",)

osaker_logger = add_custom_handler(
    logger = logging.getLogger(Colours.WHITE.apply("osaker")), 
    level = logging.INFO
)