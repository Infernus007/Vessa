# Dataset Generator

A comprehensive HTTP request dataset generator for training machine learning models to detect malicious web traffic. This tool generates realistic HTTP requests with various attack patterns and benign traffic for training security models.

## Features

- Generate realistic HTTP requests with international domain support
- Multiple attack type support:
  - SQL Injection
  - NoSQL Injection
  - GraphQL Attacks
  - JWT Attacks
  - Prototype Pollution
  - Template Injection
  - XXE Injection
  - Path Traversal
  - Command Injection
  - XSS
- International domain support for 12 regions
- Realistic header generation
- Cookie and session handling
- Form data generation
- Phishing pattern generation
- Support for modern web technologies (GraphQL, JWT, etc.)

## Installation

```bash
pip install -r requirements.txt
```

Required packages:
- pandas>=1.5.0
- tqdm>=4.65.0
- urllib3>=2.0.0

## Usage

### Basic Usage

```python
from samplehttp import generate_request

# Generate a benign request
benign_request = generate_request(index=1, is_malicious=False)

# Generate a malicious request
malicious_request = generate_request(index=2, is_malicious=True, force_attack_type="sql_injection")
```

### Converting Existing Files

```bash
# Convert text file to CSV
python samplehttp.py --convert input.txt

# Analyze HTTP samples
python samplehttp.py --analyze samples.txt
```

### Generating Datasets

```bash
# Generate a dataset with 1000 samples (30% malicious)
python samplehttp.py --samples 1000 --malicious-ratio 0.3
```

## Attack Types

The generator supports various attack patterns:

1. SQL Injection
   - Basic SQL injection
   - Union-based attacks
   - Error-based attacks
   - Time-based attacks

2. NoSQL Injection
   - MongoDB injection patterns
   - Operator injection
   - Regex injection

3. GraphQL Attacks
   - Introspection queries
   - Resource exhaustion
   - Type enumeration

4. JWT Attacks
   - Algorithm confusion
   - Token manipulation
   - Expiration bypass

5. Modern Web Attacks
   - Prototype pollution
   - Template injection
   - XXE injection

## Output Format

The generator creates CSV files with the following columns:
- Request method
- URL
- Headers
- Cookies
- Body
- Attack type (if malicious)
- Timestamp
- User agent
- IP address
- Session ID

## Sample Files

The repository includes several sample files:
- `sqli.csv`: SQL injection samples
- `path_traversal.csv`: Path traversal attacks
- `command_injection.csv`: Command injection samples
- `phishing_dataset.csv`: Phishing request patterns
- `encoding.csv`: Various encoding techniques
- `Website.csv`: Benign website requests

## Development

To contribute to the dataset generator:

1. Fork the repository
2. Create a feature branch
3. Add new attack patterns in `samplehttp.py`
4. Test with different parameters
5. Submit a pull request

## License

MIT License - see LICENSE file for details 