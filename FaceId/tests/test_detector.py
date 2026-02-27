"""
tests/test_detector.py
-----------------------
Unit tests for YOLOFaceDetector.

The torch model is mocked so no GPU or model file is needed.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest


@pytest.fixture()
def mock_yolo_model():
    """Build a minimal mock that mimics the yolov5 results object."""
    model_mock = MagicMock()
    # Simulate one detection: bbox + conf + class
    model_mock.return_value.xyxy = [
        [[50.0, 60.0, 200.0, 250.0, 0.92, 0.0]]  # one face
    ]
    return model_mock


@patch("ai.detector.yolo_face.torch.hub.load")
def test_detect_returns_boxes(mock_hub_load, mock_yolo_model, blank_frame):
    """Detector should return a list of [x1,y1,x2,y2] boxes."""
    mock_hub_load.return_value = mock_yolo_model

    from ai.detector.yolo_face import YOLOFaceDetector

    det = YOLOFaceDetector(model_path="models/v1/yolo_face.pt")
    boxes = det.detect(blank_frame)

    assert isinstance(boxes, list)
    assert len(boxes) == 1
    assert boxes[0] == [50, 60, 200, 250]


@patch("ai.detector.yolo_face.torch.hub.load")
def test_detect_filters_low_confidence(mock_hub_load, blank_frame):
    """Detections below conf_threshold should be filtered out."""
    model_mock = MagicMock()
    model_mock.return_value.xyxy = [
        [[10.0, 10.0, 50.0, 50.0, 0.2, 0.0]]  # conf 0.2 < threshold 0.5
    ]
    mock_hub_load.return_value = model_mock

    from ai.detector.yolo_face import YOLOFaceDetector

    det = YOLOFaceDetector(model_path="models/v1/yolo_face.pt")
    boxes = det.detect(blank_frame)

    assert boxes == []


@patch("ai.detector.yolo_face.torch.hub.load")
def test_detect_returns_empty_on_error(mock_hub_load, blank_frame):
    """detect() should return [] instead of raising on inference error."""
    model_mock = MagicMock()
    model_mock.side_effect = RuntimeError("CUDA OOM")
    mock_hub_load.return_value = model_mock

    from ai.detector.yolo_face import YOLOFaceDetector

    det = YOLOFaceDetector.__new__(YOLOFaceDetector)
    det.model = model_mock
    det.conf_threshold = 0.5
    det.input_size = 640
    boxes = det.detect(blank_frame)

    assert boxes == []
