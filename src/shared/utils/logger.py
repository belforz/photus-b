import sys

from loguru import logger

logger.remove()

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    sys.stderr,
    level="INFO",
    format=log_format,
    colorize=True,
    enqueue=True,  # Torna o log assíncrono, bom para performance
    backtrace=True, # Mostra o stacktrace completo em exceções
    diagnose=True # Adiciona detalhes de exceção
)
__all__ = ["logger"]
