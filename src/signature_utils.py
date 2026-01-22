import cv2
import numpy as np

def extract_features(image_path):
    """
    Loads an image and extracts ORB keypoints and descriptors.
    If descriptors are empty due to poor image quality, raises a clear error.
    Returns (keypoints, descriptors).
    """
    # Load image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
   # Check if image was loaded successfully
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    # Create ORB detector, ORB stands for Oriented FAST and Rotated BRIEF
    orb = cv2.ORB_create()
    # None means no mask is used
    keypoints, descriptors = orb.detectAndCompute(image, None)

    # If ORB fails to find descriptors, return an empty array instead of None
    if descriptors is None:
        descriptors = np.zeros((0, 32), dtype=np.uint8)
    #keypoints are the points of interest, descriptors are the feature vectors
    # Quality check 
    quality_good = len(descriptors) > 20
    
    return keypoints, descriptors, quality_good


def compare_descriptors(desc1, desc2):
    """
    Compares two ORB descriptor sets using BFMatcher.
    Returns a similarity score between 0 and 1.
    """

    # If either descriptor set is empty, similarity is zero, avoid errors
    if desc1 is None or desc2 is None or len(desc1) == 0 or len(desc2) == 0:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = bf.match(desc1, desc2)

    if len(matches) == 0:
        return 0.0

    # Sort matches by distance (lower = better)
    matches = sorted(matches, key=lambda x: x.distance)

    # Good matches threshold (empirical)
    good_matches = [m for m in matches if m.distance < 50]

    # Similarity = ratio of good matches to total matches, converted to percentage
    return (len(good_matches) / len(matches)) * 100

