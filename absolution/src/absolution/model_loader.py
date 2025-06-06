import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any, Tuple
import numpy as np

class ModelLoader:
    def __init__(self, binary_model_path: str, multi_model_path: str, device: str = None):
        """
        Initialize the model loader with paths to both models.
        
        Args:
            binary_model_path: Path to the binary classification model
            multi_model_path: Path to the multi-class classification model
            device: Device to load models on ('cuda' or 'cpu')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load binary model
        self.binary_model = AutoModelForSequenceClassification.from_pretrained(
            binary_model_path,
            use_safetensors=True
        ).to(self.device)
        self.binary_model.eval()
        self.binary_tokenizer = AutoTokenizer.from_pretrained(binary_model_path)
        
        # Load multi-class model
        self.multi_model = AutoModelForSequenceClassification.from_pretrained(
            multi_model_path
        ).to(self.device)
        self.multi_model.eval()
        
        # Energy score calculation
        self.energy_threshold = -4  # Default threshold, can be adjusted
        
    def energy_score(self, logits: torch.Tensor, T: float = 1.0) -> float:
        """Calculate energy score for OOD detection."""
        return -T * torch.logsumexp(logits / T, dim=1).item()
    
    def detect_attack(self, text: str) -> Dict[str, Any]:
        """
        Detect if the input text contains an attack and classify its type.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary containing detection results
        """
        # Tokenize input
        inputs = self.binary_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get predictions from both models
        with torch.no_grad():
            binary_out = self.binary_model(**inputs)
            multi_out = self.multi_model(**inputs)
        
        # Process binary model output
        binary_probs = torch.softmax(binary_out.logits, dim=-1)
        binary_pred = torch.argmax(binary_probs).item()  # 0=benign, 1=malicious
        
        # Process multi-class model output
        multi_probs = torch.softmax(multi_out.logits, dim=-1)
        multi_pred_idx = torch.argmax(multi_probs).item()
        multi_pred_label = self.multi_model.config.id2label[multi_pred_idx]
        
        # Calculate energy score
        energy = self.energy_score(multi_out.logits)
        
        # Decision logic
        final_label = "benign"
        confidence = 1.0
        
        # Case 1: Both models agree on malicious (1 & 1)
        if binary_pred == 1 and multi_pred_label != "benign":
            final_label = multi_pred_label if energy <= self.energy_threshold else "unknown_malware"
            confidence = multi_probs[0][multi_pred_idx].item()
        
        # Case 2: Binary says malicious, multi says benign (1 & 0)
        elif binary_pred == 1 and multi_pred_label == "benign":
            final_label = "unknown_malware" if energy > self.energy_threshold else "benign"
            confidence = binary_probs[0][1].item()
        
        # Case 3: Binary says benign, multi says malicious (0 & 1)
        elif binary_pred == 0 and multi_pred_label != "benign":
            final_label = multi_pred_label
            confidence = multi_probs[0][multi_pred_idx].item()
        
        # Case 4: Both say benign but check OOD (0 & 0)
        else:
            if energy > self.energy_threshold:
                final_label = "unknown_malware"
                confidence = energy
            else:
                final_label = "benign"
                confidence = binary_probs[0][0].item() * multi_probs[0][0].item()
        
        return {
            "final_label": final_label,
            "confidence": confidence,
            "binary_score": binary_probs.cpu().detach().numpy()[0],
            "multi_scores": multi_probs.cpu().detach().numpy()[0],
            "energy_score": energy
        }
    
    def set_energy_threshold(self, threshold: float):
        """Set the energy threshold for OOD detection."""
        self.energy_threshold = threshold 