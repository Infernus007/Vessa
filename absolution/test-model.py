from absolution.model_loader import ModelLoader

# Paths to your models — adjust to your actual paths
binary_model_path = "./Models/binary-classifier"
multi_model_path = "./Models/multi-classifier"

# Initialize loader
loader = ModelLoader(binary_model_path, multi_model_path)

# Sample input text
text = "This is a test input to detect attacks."

result = loader.detect_attack(text)
print(result)
