"""
Absolution - Machine Learning Models for Malicious HTTP Request Detection

This package provides state-of-the-art machine learning models for detecting
and classifying malicious HTTP requests, including binary and multi-class
classification with OOD detection.
"""

from .model_loader import ModelLoader, get_model_dir

__version__ = "0.1.0"
__author__ = "Jash Naik <jashnaik2004@gmail.com>, Raj Shekhar <infojar001@gmail.com>"
__all__ = ["ModelLoader", "get_model_dir"]
