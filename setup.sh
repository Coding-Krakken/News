#!/bin/bash

# News Analytics Platform - Development Startup Script

echo "==================================="
echo "News Analytics Platform"
echo "==================================="
echo ""

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  Warning: MongoDB doesn't appear to be running"
    echo "   Please start MongoDB with: mongod"
    echo ""
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "   Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "   Creating .env file from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit backend/.env and add your OPENAI_API_KEY if you want AI fact-checking"
fi

echo "   ✓ Backend ready"
cd ..

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "   Installing Node dependencies..."
    npm install
fi

echo "   ✓ Frontend ready"
cd ..

echo ""
echo "==================================="
echo "Setup complete! To start the platform:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:3000"
echo "API docs: http://localhost:8000/docs"
echo "==================================="
