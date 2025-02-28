#!/usr/bin/env bash

echo "🔧 Setting up environment..."

# Check OS Type
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍏 Detected macOS"
    PYTHON_INSTALL_CMD="brew install python@3.11 python@3.14"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    PYTHON_INSTALL_CMD="sudo apt install python3.11 python3.14 -y"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Install Python 3.11 & 3.14 if not installed
check_python_version() {
    local version=$1
    if ! command -v python$version &> /dev/null; then
        echo "⚠️ Python $version is NOT installed. Installing..."
        eval "$PYTHON_INSTALL_CMD"
    else
        echo "✅ Python $version is already installed."
    fi
}

check_python_version "3.11"
check_python_version "3.14"

# Install EnergiBridge if not found
if ! command -v energibridge &> /dev/null; then
    echo "⚡ Installing EnergiBridge..."
    git clone https://github.com/tdurieux/EnergiBridge.git
    cd EnergiBridge
    cargo build --release
    export PATH="$PWD/target/release:$PATH"
    echo "export PATH=\"$PWD/target/release:\$PATH\"" >> ~/.bashrc
    echo "export PATH=\"$PWD/target/release:\$PATH\"" >> ~/.zshrc
    cd ..
else
    echo "EnergiBridge is already installed."
fi

# Check if EnergiBridge is running
echo "🔍 Checking if EnergiBridge is running..."
if ! pgrep -x "energibridge" > /dev/null; then
    echo "⚠️ EnergiBridge is NOT running. Starting it now..."
    nohup "$ENERGIBRIDGE" > /dev/null 2>&1 &
    sleep 2  # Give it time to start
else
    echo "EnergiBridge is already running."
fi

echo "Environment setup complete!"
