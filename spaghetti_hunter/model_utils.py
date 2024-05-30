import logging
import time
from itertools import chain
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Boxes

from spaghetti_hunter.config import settings

log = logging.getLogger(__name__)


def load_model(model_path: Path) -> YOLO:
    """Load model path to a YOLO object."""

    # IDEA: don't have this function as an "app.callback"
    #   the model may not be needed for every command
    #   now it just slows the startup of rest of the commands

    log.info(f'loading YOLO model from path {model_path!s}')
    model = YOLO(model_path, task="detect")
    log.info('model loaded')
    return model


def display_results(image: Image, boxes: list[Boxes]):
    cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    for box in boxes:
        conf = round(box.conf[0].item(), 2)
        class_num = box.cls[0].item()

        log.info(f"Confidence: {conf}, Class: {class_num}")

        x1, y1, x2, y2 = (
            int(box.xyxy[0][0].item()),
            int(box.xyxy[0][1].item()),
            int(box.xyxy[0][2].item()),
            int(box.xyxy[0][3].item()),
        )

        cv2.rectangle(cv2_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            cv2_image,
            str(conf),
            (x1, y1),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

    cv2.imwrite("fail_img.jpg", cv2_image)


def detect(model: YOLO, image: Image, confidence_threshold: float = settings.confidence_threshold):
    """Detect object classes in an image using pre-trained YOLO model."""
    log.info(f'detecting objects in {image!s}')

    log.debug('converting to greyscale')
    image = image.convert("L")

    log.debug('resizing image to 640x640')
    image = image.resize((640, 640))

    log.debug('running the detection')
    start = time.perf_counter()
    results = model(
        source=image,
        save=False,
        save_conf=False,
        show=False,
        conf=confidence_threshold,
        device='cpu',
    )
    end = time.perf_counter()
    log.info(f"Detection took {round(end - start, 2)} seconds.")

    boxes = list(chain.from_iterable(result.boxes for result in results))

    return image, boxes
