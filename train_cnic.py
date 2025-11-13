from ultralytics import YOLO

# Load a pre-trained YOLOv8n model
model = YOLO("yolov8n.pt")

# Train on your dataset
model.train(
    data="dataset/data.yaml",  # path to your data.yaml
    epochs=50,                 # number of training epochs
    imgsz=640,
    batch=4,
    project="civicnics",       # folder where trained model will be saved
    name="civicnics_photo",    # subfolder for this experiment
    exist_ok=True
)
