#!/bin/bash
# Quick launcher for the GUI installer

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    echo "Please install Python 3: sudo apt-get install python3 python3-tk"
    exit 1
fi

# Check if tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: tkinter is not installed"
    echo "Please install tkinter: sudo apt-get install python3-tk"
    exit 1
fi

# Run the GUI installer
python3 nuke_installer_gui.py

