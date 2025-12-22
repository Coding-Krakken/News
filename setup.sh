#!/bin/bash

# News Analytics Platform - Development Setup Script

echo "==================================="
echo "News Analytics Platform - Setup"
echo "==================================="
echo ""
echo "Choose your development environment:"
echo "  1) Docker Compose (Recommended)"
echo "  2) Manual setup (Backend + Frontend separately)"
echo ""
read -p "Enter your choice (1 or 2): " choice
echo ""

if [ "$choice" = "1" ]; then
    echo "🐳 Setting up with Docker Compose..."
    echo ""
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Error: Docker is not running"
        echo "   Please start Docker and try again"
        exit 1
    fi
    
    # Check if docker-compose exists
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        echo "❌ Error: docker-compose is not installed"
        echo "   Please install Docker Compose and try again"
        exit 1
    fi
    
    # Create backend .env if it doesn't exist
    if [ ! -f "backend/.env" ]; then
        echo "📝 Creating backend/.env from template..."
        cp backend/.env.example backend/.env
        echo "   ⚠️  Edit backend/.env to add your OPENAI_API_KEY (optional)"
        echo ""
    fi
    
    echo "🚀 Starting all services with Docker Compose..."
    echo "   This will start MongoDB, Backend, and Frontend"
    echo ""
    
    docker-compose up
    
elif [ "$choice" = "2" ]; then
    echo "📦 Manual setup selected..."
    echo ""

    # Check if MongoDB is running
    if ! pgrep -x "mongod" > /dev/null; then
        echo "⚠️  Warning: MongoDB doesn't appear to be running"
        echo "   Please start MongoDB with: mongod"
        echo "   Or use Docker: docker run -d -p 27017:27017 mongo:7"
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
    
else
    echo "❌ Invalid choice. Please run the script again and choose 1 or 2."
    exit 1
fi

