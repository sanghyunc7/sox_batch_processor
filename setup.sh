#!/bin/bash

# Get the parent directory of the script's location
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
echo $SCRIPT_DIR

# Install required packages from apt
apt-get update && apt-get install -y libtool autoconf pkg-config gcc g++ autoconf-archive make || \
  (echo "Running apt-get update with sudo..." && sudo apt-get update && sudo apt-get install -y libtool autoconf pkg-config gcc g++ autoconf-archive make)



tar -xvf "$SCRIPT_DIR/libmad-0.15.1b.tar.gz" -C "$SCRIPT_DIR"
tar -xvf "$SCRIPT_DIR/flac-1.4.3.tar.xz" -C "$SCRIPT_DIR"
tar -xvf "$SCRIPT_DIR/lame-3.99.5.tar.gz" -C "$SCRIPT_DIR"

cd libmad-0.15.1b
./configure --prefix="$SCRIPT_DIR/local"
make clean
make install
cd ../lame-3.99.5
./configure --prefix="$SCRIPT_DIR/local"
make clean
make install
cd ../flac-1.4.3
./configure --prefix="$SCRIPT_DIR/local"
make clean
make install

# Add necessary environment variables to ~/.bashrc for future runs
echo "export PKG_CONFIG=\"$SCRIPT_DIR/local/lib/pkgconfig\"" >> ~/.bashrc
echo "export PKG_CONFIG_PATH=\"$SCRIPT_DIR/local/lib/pkgconfig\"" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=\"$SCRIPT_DIR/local/lib\"" >> ~/.bashrc
echo "export PATH=\"$PATH:$SCRIPT_DIR/local/bin\"" >> ~/.bashrc
echo "export FLAC_CFLAGS=\"-I$SCRIPT_DIR/flac-1.4.3/include\"" >> ~/.bashrc
echo "export FLAC_LIBS=\"-L$SCRIPT_DIR/local/lib -lFLAC\"" >> ~/.bashrc

# sourcing bashrc won't work in this non-interactive session
export PKG_CONFIG="$SCRIPT_DIR/local/lib/pkgconfig"
export PKG_CONFIG_PATH="$SCRIPT_DIR/local/lib/pkgconfig"
export LD_LIBRARY_PATH="$SCRIPT_DIR/local/lib"
export PATH="$PATH:$SCRIPT_DIR/local/bin"
export FLAC_CFLAGS="-I$SCRIPT_DIR/flac-1.4.3/include"
export FLAC_LIBS="-L$SCRIPT_DIR/local/lib -lFLAC"


# Clone sox repository
git clone https://github.com/sanghyunc7/sox.git "$SCRIPT_DIR/../sox" || exit 1
cd "$SCRIPT_DIR/../sox"



# Run autoreconf to generate configure script
autoreconf -ivf

# Configure and install sox
./configure LDFLAGS=-L"$SCRIPT_DIR/local/lib" CFLAGS=-I"$SCRIPT_DIR/local/include" --prefix="$SCRIPT_DIR/local" --with-mad --with-lame --enable-mp3 --enable-flac
make -s
make install && echo "SoX has been compiled and installed successfully!" || exit 1
