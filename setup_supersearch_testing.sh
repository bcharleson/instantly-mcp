#!/bin/bash
# Setup script for SuperSearch testing

set -e  # Exit on error

echo "============================================================"
echo "  SuperSearch Testing Setup"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found!"
    echo "Please run this script from the repository root."
    exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  ✅ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "  ✅ Virtual environment created"
else
    echo ""
    echo "  ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "  ✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "  ✅ pip upgraded"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -e . > /dev/null 2>&1
echo "  ✅ Dependencies installed"

# Make test scripts executable
echo ""
echo "🔧 Making test scripts executable..."
chmod +x test_supersearch.py test_supersearch_interactive.py validate_supersearch.py
echo "  ✅ Test scripts are executable"

# Run validation
echo ""
echo "🧪 Running validation..."
python validate_supersearch.py

# Check for API key
echo ""
echo "🔑 Checking for API key..."
if [ -z "$INSTANTLY_API_KEY" ]; then
    echo "  ⚠️  INSTANTLY_API_KEY not set"
    echo ""
    echo "To test with the real API, set your API key:"
    echo "  export INSTANTLY_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to a .env file:"
    echo "  echo 'INSTANTLY_API_KEY=your-api-key-here' > .env"
else
    echo "  ✅ API key found: ${INSTANTLY_API_KEY:0:10}..."
fi

echo ""
echo "============================================================"
echo "  ✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your API key (if not already set):"
echo "   export INSTANTLY_API_KEY='your-api-key-here'"
echo ""
echo "3. Run tests:"
echo "   python test_supersearch.py                    # Automated tests"
echo "   python test_supersearch_interactive.py        # Interactive menu"
echo ""
echo "4. Or validate without API calls:"
echo "   python validate_supersearch.py"
echo ""

