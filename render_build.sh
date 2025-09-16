#!/bin/bash
# Render build script
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la
echo "Installing requirements..."
pip install -r requirements.txt
echo "Build complete!"
