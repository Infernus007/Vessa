# Absolution

A state-of-the-art machine learning package for detecting and classifying malicious HTTP requests. Built with PyTorch and Transformers, Absolution provides both binary and multi-class classification capabilities with out-of-distribution detection.

## Features

- Binary Classification: Detect malicious vs. benign requests
- Multi-class Classification: Categorize different types of attacks
- Out-of-Distribution Detection: Identify novel attack patterns
- Real-time Inference: Optimized for production deployment
- Model Export: Support for ONNX and TorchScript formats

## Installation

```bash
# Using Poetry
poetry install

# Or using pip
pip install .
```

## Usage

```python
from absolution import AbsolutionClassifier

# Initialize the classifier
classifier = AbsolutionClassifier()

# Classify a request
result = classifier.classify_request(
    method="POST",
    path="/api/login",
    headers={"Content-Type": "application/json"},
    body='{"username": "admin", "password": "password123"}'
)

print(f"Classification: {result.classification}")
print(f"Confidence: {result.confidence}")
print(f"OOD Score: {result.ood_score}")
```

## Model Training

```python
from absolution import AbsolutionTrainer

# Initialize the trainer
trainer = AbsolutionTrainer(
    model_type="binary",  # or "multiclass"
    epochs=10,
    batch_size=32
)

# Train the model
trainer.train(
    train_data="path/to/train.json",
    validation_data="path/to/val.json"
)

# Save the model
trainer.save_model("path/to/save/model.pt")
```

## Development

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Run tests:
   ```bash
   poetry run pytest
   ```

3. Run linting:
   ```bash
   poetry run black .
   poetry run flake8
   poetry run mypy .
   ```

## Project Structure

```
absolution/
├── src/
│   └── absolution/
│       ├── models/         # Model architectures
│       ├── data/          # Data processing utilities
│       ├── training/      # Training scripts
│       └── inference/     # Inference utilities
├── tests/                 # Test suite
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details 