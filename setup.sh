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


#!/bin/bash

# Step 1: Extract sox_installation.tar.gz and mv directory 'local' to ~
tar -xzf sox_installation.tar.gz
mv local ~

# Step 2: Download and install dependencies
# LAME
wget -O lame-3.99.5.tar.gz "http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Flame%2Ffiles%2Flame%2F3.99%2F&ts=1416316457&use_mirror=kent"
tar -xf lame-3.99.5.tar.gz
cd lame-3.99.5
./configure --prefix=/home/dan/local
make clean
make install
cd ..

# FLAC
wget -O flac-1.4.3.tar.xz "https://ftp.osuosl.org/pub/xiph/releases/flac/flac-1.4.3.tar.xz"
tar -xf flac-1.4.3.tar.xz
cd flac-1.4.3
./configure --prefix=/home/dan/local
make clean
make install
cd ..

# MAD
wget -O libmad-0.15.1b.tar.gz "https://sourceforge.net/projects/mad/files/libmad/0.15.1b/libmad-0.15.1b.tar.gz/download"
tar -xf libmad-0.15.1b.tar.gz
cd libmad-0.15.1b
# There was a compilation error, the link provided has a workaround
# referring to a StackOverflow question
# You can address it manually
./configure --prefix=/home/dan/local
make clean
make install
cd ..

# Step 3: Compiling sox
# Add necessary environment variables to ~/.bashrc and source it
echo 'export PKG_CONFIG="/home/dan/local/lib/pkgconfig"' >> ~/.bashrc
echo 'export PKG_CONFIG_PATH="/home/dan/local/lib/pkgconfig"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/home/dan/local/lib:/home' >> ~/.bashrc
echo 'export PATH=${PATH}:/home/dan/local/bin' >> ~/.bashrc
echo 'export FLAC_CFLAGS="-I/home/dan/flac-1.4.3/include"' >> ~/.bashrc
echo 'export FLAC_LIBS="-L/home/dan/local/lib -lFLAC"' >> ~/.bashrc
source ~/.bashrc

# Clone sox repository
git clone https://github.com/rhgg2/sox.git
cd sox

# Install required packages from apt
# sudo apt-get install libtool autoconf pkg-config g++ autoconf-archive make

# Run autoreconf to generate configure script
autoreconf -ivf

# Configure and install sox
./configure LDFLAGS=-L/home/dan/local/lib CFLAGS=-I/home/dan/local/include --prefix=/home/dan/local --with-mad --with-lame --enable-mp3 --enable-flac
make -s
make install

# Clean up
cd ..
rm -rf lame-3.99.5 flac-1.4.3 libmad-0.15.1b sox sox_installation.tar.gz

echo "SoX has been compiled and installed successfully!"
