import streamlit as st
from signature_utils import compare_all_signatures, extract_text_from_image
import cv2
import numpy as np

# ---------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Signature Recognition App",
    layout="centered"
)

# ---------------------------------------------------------
# App Title and Description
# ---------------------------------------------------------
st.title("🔍 Signature Recognition System")
st.write("Upload a signature image to identify the most likely matching name from the database.")

# ---------------------------------------------------------
# File uploader (accepts PNG, JPG, JPEG)
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Choose a signature image",
    type=["png", "jpg", "jpeg"]
)

# ---------------------------------------------------------
# If the user uploads a file, process it
# ---------------------------------------------------------
if uploaded_file is not None:

    # Convert uploaded file to an OpenCV image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Display the uploaded image
    st.image(img, channels="BGR", caption="Uploaded Signature")

    # Save temporarily so the recognition functions can read it
    temp_path = "temp_signature.png"
    cv2.imwrite(temp_path, img)

    # ---------------------------------------------------------
    # OCR Section — Show extracted text
    # ---------------------------------------------------------
    st.subheader("📘 OCR Result (Extracted Text)")
    text = extract_text_from_image(temp_path)

    if text:
        st.success(f"Detected text: **{text}**")
    else:
        st.warning("No readable text detected in the image.")

    # ---------------------------------------------------------
    # Signature Recognition Section
    # ---------------------------------------------------------
    st.subheader("📊 Signature Identification Results")

    result = compare_all_signatures(temp_path)

    # Display top 3 matches
    for name, score in result["top_3_matches"]:
        st.write(f"**{name}** — {score:.1f}% similarity")
