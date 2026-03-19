#!/bin/bash
set -e

# Setup Fish shell configuration for Starship
mkdir -p ~/.config/fish
if ! grep -q "starship init fish" ~/.config/fish/config.fish 2>/dev/null; then
    echo 'starship init fish | source' >> ~/.config/fish/config.fish
fi

# Install Gemini CLI
npm install -g @google/gemini-cli

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install Python development dependencies
pip install -r requirements-dev.txt
