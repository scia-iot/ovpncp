#!/bin/bash
set -e

# Setup Fish shell configuration for Starship
mkdir -p ~/.config/fish
if ! grep -q "starship init fish" ~/.config/fish/config.fish 2>/dev/null; then
    echo 'starship init fish | source' >> ~/.config/fish/config.fish
fi
starship preset bracketed-segments -o ~/.config/starship.toml

# Install Gemini CLI
npm install -g @google/gemini-cli

# Install Python development dependencies
pip install -r requirements-dev.txt
