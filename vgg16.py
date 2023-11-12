import os
import torch
import pandas as pd
from tqdm import tqdm
from PIL import Image
from torchvision.models import vgg16
import torchvision.transforms as transforms


data_path = 'data/'
image_path = 'datathon/images/'

products = pd.read_csv(data_path + 'products_clean.csv')
outfits = pd.read_csv('datathon/dataset/outfit_data.csv')


if not os.path.exists(data_path + 'image_features.csv'):
    # Load pre-trained VGG model
    model = vgg16(pretrained=True)
    # Remove the classification layer (fc) for feature extraction
    model.classifier = model.classifier[:-1]
    # Set model to evaluation mode
    model.eval()


def preprocess_image(image):
    """
    Returns the preprocessed image.
    
    Parameters
    ----------
    image_path : str
        Path to the image.
    
    Returns
    -------
    numpy.ndarray
        Preprocessed image.
    """

    image = Image.open(image).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = preprocess(image)
    image = image.unsqueeze(0)
    return image


def extract_features(image):
    """
    Returns the features of an image.

    Parameters
    ----------
    image_path : str
        Path to the image.
    
    Returns
    -------
    numpy.ndarray
        Features of the image.
    """
    
    preprocessed = preprocess_image(image)
    with torch.no_grad():
        features = model(preprocessed)
    return features.squeeze().numpy()


def compute_image_features():
    """
    Computes the features of all the images in a directory and saves them to a file.

    Returns
    -------
    pandas.DataFrame
        Dataframe containing the features of all the images.
    """

    # if image_features.csv exists, load it and return it
    if os.path.exists(data_path + 'image_features.csv'):
        return pd.read_csv(data_path + 'image_features.csv', index_col=0)

    # Get a list of all the image files in the directory
    image_files = [f for f in os.listdir(image_path) if os.path.isfile(os.path.join(image_path, f))]

    # Create an empty dictionary to store the features
    features_dict = {}

    # Iterate through the image files and extract the features
    for image_file in tqdm(image_files):
        image = os.path.join(image_path, image_file)
        features = extract_features(image)
        features_dict[image_file] = features

    # Convert the dictionary to a pandas dataframe
    features_df = pd.DataFrame.from_dict(features_dict, orient='index')

    # Save the features to a file
    features_df.to_csv(data_path + 'image_features.csv')

    return features_df