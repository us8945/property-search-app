import logging
import os
from datetime import datetime


def setup_logger(debug_flag=logging.INFO):
    # Get the Gradio logger
    gradio_logger = logging.getLogger("gradio")
    gradio_logger.setLevel(debug_flag)

    # Remove existing handlers to prevent duplicate logs
    for handler in gradio_logger.handlers[:]:
        gradio_logger.removeHandler(handler)

    # Create a logs folder
    current_file_path = os.path.abspath(__file__)
    two_levels_up = os.path.dirname(os.path.dirname(current_file_path))
    logs_folder = os.path.join(two_levels_up, "logs")
    os.makedirs(logs_folder, exist_ok=True)

    # Add a file handler
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(
        os.path.join(logs_folder, f"app_{timestamp}.log")
    )
    file_handler.setLevel(debug_flag)

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(debug_flag)

    # Set a formatter with timestamps
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    gradio_logger.addHandler(file_handler)
    gradio_logger.addHandler(console_handler)

    # Prevent duplicate logs from propagation
    gradio_logger.propagate = False

    return gradio_logger


# Initialize the logger and make it accessible
logger = setup_logger()
