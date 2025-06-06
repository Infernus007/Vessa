# Absolution: Advanced HTTP Request Security Models

## Overview
Absolution is a pair of state-of-the-art machine learning models designed for detecting and classifying malicious HTTP requests. The system consists of two specialized models: a binary classifier for initial threat detection and a multi-class classifier for detailed attack categorization, enhanced with energy-based out-of-distribution (OOD) detection capabilities. Both models are fine-tuned versions of Google's BERT (Bidirectional Encoder Representations from Transformers) architecture.

## Model Architecture

### 1. Binary Classification Model
- **Base Model**: Fine-tuned Google BERT
- **Purpose**: Initial screening of requests to determine if they are malicious or benign
- **Architecture**: BERT-based sequence classification with custom fine-tuning
- **Output**: Binary classification (benign/malicious) with confidence scores
- **Key Features**:
  - Fast initial screening
  - High precision in distinguishing between safe and malicious requests
  - Optimized for real-time processing
  - Leverages BERT's powerful contextual understanding
  - Custom fine-tuning for HTTP request patterns

### 2. Multi-class Classification Model
- **Base Model**: Fine-tuned Google BERT
- **Purpose**: Detailed classification of malicious requests into specific attack types
- **Architecture**: BERT-based multi-class classification with custom fine-tuning
- **Output**: Classification into 19 attack categories:
  - XSS (Cross-Site Scripting)
  - SQL Injection
  - Path Traversal
  - SSRF (Server-Side Request Forgery)
  - JWT Attacks
  - GraphQL Attacks
  - Template Injection
  - Modern CMDI
  - Modern File Attacks
  - Modern SQLi
  - Modern SSRF
  - Modern XSS
  - NoSQL Injection
  - Open Redirect
  - Prototype Pollution
  - XXE Injection
  - Deserialization
  - And more...
- **Key Features**:
  - Fine-grained attack classification
  - High accuracy in identifying specific attack patterns
  - Comprehensive coverage of modern web attack vectors
  - Support for both traditional and modern attack patterns
  - BERT's bidirectional context understanding for complex attack patterns

### 3. Energy-Based OOD Detection
- **Purpose**: Identify unknown or novel attack patterns
- **Method**: Energy score calculation using BERT logits
- **Features**:
  - Detects previously unseen attack patterns
  - Adaptable to new attack vectors
  - Configurable sensitivity levels
  - Temperature-based uncertainty calibration
  - Leverages BERT's rich feature representations

## Technical Specifications

### Model Input Format
```
[METHOD] {method}
[URL] {url}
[COOKIE] {cookie}
[BODY] {body}
[HOST] {host}
[USER_AGENT] {user_agent}
[X_FORWARDED_FOR] {x_forwarded_for}
[REFERER] {referer}
[X_REQUESTED_WITH] {x_requested_with}
[ACCEPT_LANG] {accept_language}
[HTTP_VERSION] {http_version}
```

### Processing Pipeline
1. Input normalization and formatting
2. BERT tokenization and embedding
3. Binary classification for initial screening
4. Multi-class classification for attack categorization
5. Energy score calculation for OOD detection
6. Confidence-based decision logic

### Model Parameters
- Base Model: Google BERT
- Maximum sequence length: 512 tokens
- Temperature parameter (T): 1.0 (configurable)
- Device selection: Automatic (CPU/GPU)
- Batch size: Optimized for real-time processing
- Fine-tuning epochs: Customized for HTTP security patterns

## Model Performance

### Inference Characteristics
- Average inference time: < 100ms
- Memory footprint: ~500MB (both models)
- GPU memory requirement: ~1GB (with CUDA)
- CPU memory requirement: ~2GB (without CUDA)

### Detection Metrics
- Binary classification accuracy: >95%
- Multi-class classification F1-score: >90%
- OOD detection rate: >85%

## Configuration Options

### Energy Thresholds
- **Strict Security** (-3): Low false positive rate
- **Balanced** (-4): Default setting
- **High Sensitivity** (-7): Low false negative rate

### Model Customization
- Adjustable temperature parameter for energy calculation
- Configurable sequence length
- Customizable confidence thresholds
- Flexible device placement (CPU/GPU)
- BERT-specific hyperparameter tuning

## Requirements
- Python 3.8+
- PyTorch 2.1.0+
- Transformers 4.35.0+
- CUDA support (optional, for GPU acceleration)

## Best Practices
1. Regular model updates with new attack patterns
2. Periodic threshold calibration based on deployment environment
3. Continuous monitoring of detection rates
4. Regular validation against new attack patterns
5. Proper input sanitization and normalization
6. Regular model performance evaluation
7. Backup and version control of model weights
8. BERT-specific fine-tuning maintenance 