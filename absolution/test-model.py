import sys
import os
from pathlib import Path

# Add the src directory to the Python path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from absolution.model_loader import ModelLoader

# Use relative paths for now
binary_model_path = "./src/absolution/Models/binary-classifier"
multi_model_path = "./src/absolution/Models/multi-classifier"

print(f"Loading models from:")
print(f"  Binary model: {binary_model_path}")
print(f"  Multi-class model: {multi_model_path}")
print()

# Initialize loader
loader = ModelLoader(binary_model_path, multi_model_path)

# Test inputs - various types of requests
test_cases = [
    {
        "name": "Benign HTTP Request",
        "text": "GET /index.html HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
    },
    {
        "name": "SQL Injection Attack",
        "text": "POST /api/login HTTP/1.1\r\nHost: evil.com\r\nContent-Length: 100\r\n\r\nusername=admin' OR 1=1--&password=123"
    },
    {
        "name": "SSRF Attack",
        "text": "GET /?url=http://169.254.169.254/latest/meta-data/ HTTP/1.1\r\nHost: victim.com\r\n\r\n"
    },
    {
        "name": "XSS Attack",
        "text": "GET /search?q=<script>alert('xss')</script> HTTP/1.1\r\nHost: target.com\r\n\r\n"
    },
    {
        "name": "Path Traversal",
        "text": "GET /../../../etc/passwd HTTP/1.1\r\nHost: vulnerable.com\r\n\r\n"
    },
    {
        "name": "Generic Text",
        "text": "This is a test input to detect attacks."
    }
]

print("Testing models with various inputs:")
print("=" * 60)

for i, case in enumerate(test_cases, 1):
    print(f"\n{i}. {case['name']}")
    print(f"Input: {case['text'][:100]}{'...' if len(case['text']) > 100 else ''}")
    
    try:
        result = loader.detect_attack(case['text'])
        
        print(f"Final Label: {result['final_label']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Energy Score: {result['energy_score']:.4f}")
        print(f"Binary Scores: [benign: {result['binary_score'][0]:.4f}, malicious: {result['binary_score'][1]:.4f}]")
        print(f"Multi-class Scores: {dict(zip(range(len(result['multi_scores'])), [f'{score:.4f}' for score in result['multi_scores']]))}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 60)

print("\nTesting completed!")
