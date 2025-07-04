import streamlit as st
import torch
from models import SeatBelt
import torchvision.transforms as transforms
from PIL import Image

# Title
st.title("Seatbelt Compliance Detection")

# Load the trained model
model = SeatBelt()
model.load_state_dict(torch.load("models/seatbelt.pt", map_location=torch.device('cpu')))
model.eval()

# Class names (based on your dataset)
class_names = ["Worn", "Not Worn", "Not Detected"]

# Image transformation (must match training input size)
transform = transforms.Compose([
    transforms.Resize((320, 320)),  # important for 6 pooling layers
    transforms.ToTensor()
])

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    input_tensor = transform(image).unsqueeze(0)  # shape: [1, 3, 320, 320]

    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        label = class_names[predicted_class]

        st.write("Probabilities:", probabilities.numpy())

    # Show status
    if label == "Worn":
        st.success(f"Seatbelt Status: {label}")
    elif label == "Not Worn":
        st.error(f"Seatbelt Status: Not detected")
    else:
        st.warning(f"Seatbelt Status: Not detected")

        
