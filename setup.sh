#!/bin/bash

# Get the parent directory of the script's location
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# Step 1: Extract sox_installation.tar.gz
tar -xzvf "$SCRIPT_DIR/sox_installation.tar.gz" -C "$SCRIPT_DIR"

# Step 3: Compiling sox
# Add necessary environment variables to ~/.bashrc
echo "export PKG_CONFIG=\"$SCRIPT_DIR/local/lib/pkgconfig\"" >> ~/.bashrc
echo "export PKG_CONFIG_PATH=\"$SCRIPT_DIR/local/lib/pkgconfig\"" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=\"$SCRIPT_DIR/local/lib\"" >> ~/.bashrc
echo "export PATH=\"$PATH:$SCRIPT_DIR/local/bin\"" >> ~/.bashrc
echo "export FLAC_CFLAGS=\"-I$SCRIPT_DIR/flac-1.4.3/include\"" >> ~/.bashrc
echo "export FLAC_LIBS=\"-L$SCRIPT_DIR/local/lib -lFLAC\"" >> ~/.bashrc

# sourcing bashrc won't work in a non-interactive session
export PKG_CONFIG="$SCRIPT_DIR/local/lib/pkgconfig"
export PKG_CONFIG_PATH="$SCRIPT_DIR/local/lib/pkgconfig"
export LD_LIBRARY_PATH="$SCRIPT_DIR/local/lib"
export PATH="$PATH:$SCRIPT_DIR/local/bin"
export FLAC_CFLAGS="-I$SCRIPT_DIR/flac-1.4.3/include"
export FLAC_LIBS="-L$SCRIPT_DIR/local/lib -lFLAC"

echo "hello world!"
echo $FLAC_LIBS
echo "goodbye!"

# Clone sox repository
if ! git clone https://github.com/rhgg2/sox.git "$SCRIPT_DIR/../sox"; then
    echo "Error: Failed to clone SoX repository"
    exit 1
fi
cd "$SCRIPT_DIR/../sox" || exit 1

# Install required packages from apt
apt-get update && apt-get install -y libtool autoconf pkg-config g++ autoconf-archive make || sudo apt-get update && sudo apt-get install -y libtool autoconf pkg-config g++ autoconf-archive make


# Run autoreconf to generate configure script
autoreconf -ivf

# Configure and install sox
./configure LDFLAGS=-L"$SCRIPT_DIR/local/lib" CFLAGS=-I"$SCRIPT_DIR/local/include" --prefix="$SCRIPT_DIR/local" --with-mad --with-lame --enable-mp3 --enable-flac
make -s
make install

echo "SoX has been compiled and installed successfully!"
