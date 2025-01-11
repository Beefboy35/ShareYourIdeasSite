
import logging
import sys

from starlette import status
from starlette.responses import JSONResponse


def get_logger():
    """Создаёт и настраивает логгер."""
    logger = logging.getLogger("my_app")
    logger.setLevel(logging.INFO)  # Устанавливает уровень логов

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
    )

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


    # Логгирование в файл (важно для производства)
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log_exception(logger, request_info, exc_info=None):
  """Логирует исключения с контекстом запроса."""
  if exc_info:
    logger.exception(f"Error: {request_info}")
  else:
    logger.error(f"Error: {request_info}")


def log_request(logger, request_info):
    logger.info(f"Request: {request_info}")


def log_response(logger, response_status, response_info):
    logger.info(f"Response: {response_status} Additional Info: {response_info}")


def log_and_return_error_response(logger, request_info, exc_info=None, error_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
  """Логирует ошибку и возвращает JSONResponse с ошибкой."""
  log_exception(logger, request_info, exc_info)
  return JSONResponse(status_code=error_status_code, content={"detail": "Ошибка сервера"})