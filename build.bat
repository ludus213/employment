echo "Installing dependencies..."
pip install -r requirements.txt

echo "Building executable..."
pyinstaller --onefile --noconsole --add-data="j-slur.png:." j_slurpreventer.py

echo "Cleaning up..."
rm -f *.spec
rm -rf build

echo "Build complete! The executable is in the 'dist' folder."
