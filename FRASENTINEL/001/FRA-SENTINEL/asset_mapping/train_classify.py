import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import rasterio
from rasterio.transform import from_bounds
import os

def load_or_create_satellite_image():
    """Load satellite image or create dummy data"""
    try:
        # Try to load real satellite image
        with rasterio.open("../data/sentinel_image.tif") as src:
            img = src.read()
        print("Loaded real satellite image")
    except:
        # Create dummy satellite image
        print("Creating dummy satellite image...")
        np.random.seed(42)
        height, width = 100, 100
        
        # Create realistic patterns
        red = np.random.randint(50, 200, (height, width), dtype=np.uint8)
        green = np.random.randint(30, 180, (height, width), dtype=np.uint8) 
        blue = np.random.randint(20, 150, (height, width), dtype=np.uint8)
        nir = np.random.randint(100, 255, (height, width), dtype=np.uint8)
        
        # Add some patterns for different land types
        # Forest area (high NIR, moderate green)
        red[20:40, 20:40] = 80
        green[20:40, 20:40] = 120
        blue[20:40, 20:40] = 60
        nir[20:40, 20:40] = 200
        
        # Water area (low NIR, high blue)
        red[60:80, 60:80] = 40
        green[60:80, 60:80] = 60
        blue[60:80, 60:80] = 150
        nir[60:80, 60:80] = 20
        
        img = np.stack([red, green, blue, nir], axis=0)
        
        # Save as GeoTIFF for later use
        transform = from_bounds(75.6, 21.8, 75.7, 21.9, width, height)
        with rasterio.open("../data/sentinel_image.tif", "w", 
                          driver="GTiff", height=height, width=width,
                          count=4, dtype=img.dtype, crs="EPSG:4326",
                          transform=transform) as dst:
            dst.write(img)
    
    return img

def prepare_training_data(img, labels_file):
    """Prepare training data from labeled pixels"""
    # Load training labels
    labels = pd.read_csv(labels_file)
    
    n_bands, height, width = img.shape
    
    # Extract features for labeled pixels
    X_train = []
    y_train = []
    
    for _, row in labels.iterrows():
        r, c = int(row['row']), int(row['col'])
        if r < height and c < width:
            # Extract pixel values across all bands
            pixel_values = img[:, r, c]
            X_train.append(pixel_values)
            y_train.append(row['class_id'])
    
    return np.array(X_train), np.array(y_train)

def train_classifier(X_train, y_train):
    """Train Random Forest classifier"""
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf

def classify_entire_image(img, classifier):
    """Apply classifier to entire image"""
    n_bands, height, width = img.shape
    
    # Reshape image to (n_pixels, n_bands)
    X = img.reshape(n_bands, -1).T
    
    # Predict
    y_pred = classifier.predict(X)
    
    # Reshape back to image dimensions
    classified = y_pred.reshape(height, width)
    
    return classified

def save_classified_image(classified_img, output_path):
    """Save classified image as GeoTIFF"""
    height, width = classified_img.shape
    transform = from_bounds(75.6, 21.8, 75.7, 21.9, width, height)
    
    with rasterio.open(output_path, "w", 
                      driver="GTiff", height=height, width=width,
                      count=1, dtype=classified_img.dtype, 
                      crs="EPSG:4326", transform=transform) as dst:
        dst.write(classified_img.astype(rasterio.uint8), 1)

def visualize_results(img, classified_img):
    """Create visualization"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image (RGB composite)
    rgb = np.stack([img[0], img[1], img[2]], axis=2)
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min())  # Normalize
    axes[0].imshow(rgb)
    axes[0].set_title("Original RGB Image")
    axes[0].axis('off')
    
    # NIR band
    axes[1].imshow(img[3], cmap='RdYlGn')
    axes[1].set_title("Near-Infrared Band")
    axes[1].axis('off')
    
    # Classified image
    class_colors = ['yellow', 'green', 'blue', 'red']  # farmland, forest, water, homestead
    axes[2].imshow(classified_img, cmap='tab10', vmin=0, vmax=3)
    axes[2].set_title("Land Use Classification")
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig("../data/classification_results.png", dpi=150, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    # Load satellite image
    print("Loading satellite image...")
    img = load_or_create_satellite_image()
    print(f"Image shape: {img.shape}")
    
    # Prepare training data
    print("Preparing training data...")
    X_train, y_train = prepare_training_data(img, "../data/training_labels.csv")
    print(f"Training samples: {len(X_train)}")
    
    # Train classifier
    print("Training classifier...")
    classifier = train_classifier(X_train, y_train)
    
    # Classify entire image
    print("Classifying entire image...")
    classified_img = classify_entire_image(img, classifier)
    
    # Save results
    output_path = "../data/classified_map.tif"
    save_classified_image(classified_img, output_path)
    print(f"Classified image saved: {output_path}")
    
    # Calculate class statistics
    unique, counts = np.unique(classified_img, return_counts=True)
    total_pixels = classified_img.size
    
    class_names = ['Farmland', 'Forest', 'Water', 'Homestead']
    print("\nLand use statistics:")
    for class_id, count in zip(unique, counts):
        percentage = (count / total_pixels) * 100
        print(f"{class_names[class_id]}: {percentage:.1f}% ({count} pixels)")
    
    # Visualize results
    visualize_results(img, classified_img)
    
    print("Asset mapping complete!")
