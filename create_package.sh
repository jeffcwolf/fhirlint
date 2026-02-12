#!/bin/bash
# Create a portable package of the FHIR Quality Inspector

echo "📦 Creating portable package..."

cd /work

# Create tarball excluding unnecessary files
tar -czf fhir-inspector-package.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='.claude' \
  --exclude='work' \
  src/ \
  data/ \
  messy_data/ \
  output/ \
  _docs/ \
  *.py \
  *.sh \
  *.bat \
  *.md \
  *.txt

echo "✅ Package created: /work/fhir-inspector-package.tar.gz"
echo ""
echo "📋 To extract on your local machine:"
echo "   1. Copy this file from the container to your machine"
echo "   2. tar -xzf fhir-inspector-package.tar.gz"
echo "   3. cd into the directory"
echo "   4. python3 -m venv venv && source venv/bin/activate"
echo "   5. pip install fhir.resources matplotlib"
echo "   6. python src/main.py"
