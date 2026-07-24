from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import base64
import io
import os

app = FastAPI()

# Allow React frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Define the exact same CNN Architecture used in training
class EmotionCNN(nn.Module):
    def __init__(self, num_classes=7):
        super(EmotionCNN, self).__init__()
        self.block1 = nn.Sequential(
            nn.Conv2d(1, 32, 3, 1, 1), nn.BatchNorm2d(32), nn.ReLU(), 
            nn.Conv2d(32, 64, 3, 1, 1), nn.BatchNorm2d(64), nn.ReLU(), 
            nn.MaxPool2d(2, 2), nn.Dropout(0.25)
        )
        self.block2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, 1, 1), nn.BatchNorm2d(128), nn.ReLU(), 
            nn.Conv2d(128, 128, 3, 1, 1), nn.BatchNorm2d(128), nn.ReLU(), 
            nn.MaxPool2d(2, 2), nn.Dropout(0.25)
        )
        self.block3 = nn.Sequential(
            nn.Conv2d(128, 256, 3, 1, 1), nn.BatchNorm2d(256), nn.ReLU(), 
            nn.MaxPool2d(2, 2), nn.Dropout(0.25)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(), 
            nn.Linear(256 * 6 * 6, 256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.5), 
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        return self.classifier(self.block3(self.block2(self.block1(x))))

# 2. Load the model globally when the server starts
device = torch.device('cpu')
model = EmotionCNN(num_classes=7).to(device)

# Resolve path relative to this backend folder
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_emotion_cnn.pth')
try:
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print("SUCCESS: Successfully loaded PyTorch model weights!")
except Exception as e:
    print(f"ERROR: Failed to load model weights: {e}")

# Class labels
classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((48, 48)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

class ImageData(BaseModel):
    image_base64: str

@app.get("/")
def read_root():
    return {"status": "Backend API is running and Model is loaded!"}

@app.post("/predict")
def predict_emotion(data: ImageData):
    try:
        # Strip the data URI header if present (e.g., "data:image/jpeg;base64,")
        encoded_data = data.image_base64
        if ',' in encoded_data:
            encoded_data = encoded_data.split(',')[1]
            
        # Decode the base64 string into bytes
        image_bytes = base64.b64decode(encoded_data)
        
        # Load it into a PIL Image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Apply transforms and add batch dimension
        input_tensor = preprocess(img)
        input_batch = input_tensor.unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            output = model(input_batch)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
        # Map probabilities to classes
        probs_dict = {classes[i]: float(probabilities[i].item() * 100) for i in range(len(classes))}
        sorted_probs = dict(sorted(probs_dict.items(), key=lambda item: item[1], reverse=True))
        
        predicted_class = list(sorted_probs.keys())[0]
        confidence = list(sorted_probs.values())[0]
        
        return {
            "prediction": predicted_class,
            "confidence": confidence,
            "probabilities": sorted_probs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
