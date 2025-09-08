#!/bin/bash

# setup.sh - Complete setup script for StarLinks application

set -e  # Exit on any error

echo "🌟 Setting up StarLinks application..."
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+ and try again."
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ pip3 is required but not installed. Please install pip and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Create project structure if it doesn't exist
echo "📁 Creating project structure..."

mkdir -p backend frontend data docs tests scripts
mkdir -p frontend/css frontend/js frontend/assets/images frontend/assets/icons

# Create __init__.py files
touch backend/__init__.py tests/__init__.py

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found. Installing basic dependencies..."
    pip install flask flask-cors networkx requests tqdm python-dotenv
fi

# Create .env file if it doesn't exist
echo "🔧 Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
        echo "⚠️  Please edit .env file and add your TMDb API key"
    else
        echo "⚠️  .env.example not found. Please create .env file manually"
    fi
else
    echo "✅ .env file already exists"
fi

# Check for data files
echo "📊 Checking data files..."
DATA_FILES_EXIST=true

if [ ! -f "data/people.csv" ]; then
    echo "⚠️  data/people.csv not found"
    DATA_FILES_EXIST=false
fi

if [ ! -f "data/movies.csv" ]; then
    echo "⚠️  data/movies.csv not found"
    DATA_FILES_EXIST=false
fi

if [ ! -f "data/stars.csv" ]; then
    echo "⚠️  data/stars.csv not found"
    DATA_FILES_EXIST=false
fi

if [ "$DATA_FILES_EXIST" = true ]; then
    echo "✅ Data files found"
    
    # Check if graph exists, if not build it
    if [ ! -f "data/graph.pkl" ]; then
        echo "🔗 Building graph from data files..."
        if [ -f "backend/build_graph.py" ]; then
            python backend/build_graph.py
            echo "✅ Graph built successfully"
        else
            echo "⚠️  backend/build_graph.py not found. Please build graph manually"
        fi
    else
        echo "✅ Graph file already exists"
    fi
else
    echo "⚠️  Data files missing. You may need to run the scraper first:"
    echo "     python backend/scraper.py"
fi

# Set permissions
chmod +x setup.sh

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your TMDb API key"
echo "2. If data files are missing, run: python backend/scraper.py"
echo "3. Start the API server: python backend/api.py"
echo "4. Open frontend/index.html in your browser"
echo ""
echo "🔗 Useful commands:"
echo "   Start server:     python backend/api.py"
echo "   Build graph:      python backend/build_graph.py" 
echo "   Scrape data:      python backend/scraper.py"
echo "   Test CLI:         python backend/degrees.py"
echo ""
echo "📍 The API will be available at: http://localhost:5001"
echo ""

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✨ Ready to go! Activate your virtual environment with: source venv/bin/activate"