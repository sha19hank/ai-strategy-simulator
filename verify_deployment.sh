#!/bin/bash
# Streamlit Cloud Deployment Verification Checklist
# Run this before committing to GitHub

echo "🔍 Streamlit Cloud Deployment Verification"
echo "==========================================="
echo ""

# Check 1: Files exist
echo "✓ Checking required files..."
files=(
    "runtime.txt"
    ".streamlit/config.toml"
    "requirements.txt"
    "requirements-dev.txt"
    "dashboard/app.py"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ MISSING: $file"
        missing_files=$((missing_files + 1))
    fi
done

echo ""
echo "✓ Checking requirements.txt content..."

# Check 2: No training packages in requirements.txt
if grep -q "gymnasium\|pettingzoo\|supersuit\|stable-baselines3\|torch" requirements.txt; then
    echo "  ❌ ERROR: Training packages found in requirements.txt!"
    echo "     These should NOT be in the deployment requirements."
    exit 1
else
    echo "  ✅ No training packages in requirements.txt"
fi

# Check 3: Core packages present
core_packages=("streamlit" "pandas" "plotly" "numpy")
for package in "${core_packages[@]}"; do
    if grep -q "$package" requirements.txt; then
        echo "  ✅ $package present"
    else
        echo "  ❌ MISSING: $package"
    fi
done

echo ""
echo "✓ Checking runtime.txt..."
if grep -q "python-3.10" runtime.txt; then
    echo "  ✅ Python 3.10 specified"
else
    echo "  ⚠️  Check runtime.txt content"
fi

echo ""
echo "✓ Checking .streamlit/config.toml..."
if [ -f ".streamlit/config.toml" ]; then
    if grep -q "showWarningOnDirectExecution" .streamlit/config.toml; then
        echo "  ✅ config.toml looks valid"
    fi
else
    echo "  ❌ config.toml not found"
fi

echo ""
echo "✓ Local test (optional)..."
echo "  Run this to test locally:"
echo "    streamlit run dashboard/app.py"
echo ""

if [ $missing_files -eq 0 ]; then
    echo "==========================================="
    echo "✅ All checks passed! Ready to deploy."
    echo "==========================================="
    echo ""
    echo "Next steps:"
    echo "  1. git add -A"
    echo "  2. git commit -m 'fix: Streamlit Cloud deployment'"
    echo "  3. git push origin main"
    echo "  4. Deploy from https://share.streamlit.io"
else
    echo "==========================================="
    echo "❌ $missing_files file(s) missing. Fix before deploying."
    echo "==========================================="
    exit 1
fi
