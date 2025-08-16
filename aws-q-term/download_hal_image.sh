#!/bin/bash

# Helper script to download the HAL 9000 panel image
# Attribution: By Tom Cowap - Own work, CC BY-SA 4.0
# https://commons.wikimedia.org/w/index.php?curid=103068276

echo "Downloading HAL 9000 Panel Image..."
echo "Attribution: By Tom Cowap - Own work, CC BY-SA 4.0"
echo "Source: https://commons.wikimedia.org/w/index.php?curid=103068276"
echo ""

# Create assets directory if it doesn't exist
mkdir -p assets

# Download the image
IMAGE_URL="https://upload.wikimedia.org/wikipedia/commons/f/f6/Hal_9000_Panel.svg.png"
OUTPUT_FILE="assets/Hal_9000_Panel.svg.png"

if command -v wget &> /dev/null; then
    echo "Using wget to download..."
    wget -O "$OUTPUT_FILE" "$IMAGE_URL"
elif command -v curl &> /dev/null; then
    echo "Using curl to download..."
    curl -L -o "$OUTPUT_FILE" "$IMAGE_URL"
else
    echo "Error: Neither wget nor curl found."
    echo "Please install wget or curl, or manually download the image from:"
    echo "$IMAGE_URL"
    echo "Save it as: $OUTPUT_FILE"
    exit 1
fi

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "HAL image downloaded successfully to: $OUTPUT_FILE"
    echo "You can now run the HAL interface with full visual experience!"
else
    echo ""
    echo "Download failed. Please manually download the image from:"
    echo "$IMAGE_URL"
    echo "Save it as: $OUTPUT_FILE"
fi
