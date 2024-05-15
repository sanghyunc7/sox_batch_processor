# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04


# Update package lists and install git
RUN apt-get update && apt-get install -y git
# only for docker
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get update && apt-get install -y libtool autoconf pkg-config gcc g++ autoconf-archive make || \
  (echo "Running apt-get update with sudo..." && sudo apt-get update && sudo apt-get install -y libtool autoconf pkg-config gcc g++ autoconf-archive make)


# Clone the repository
RUN git clone https://github.com/sanghyunc7/sox_batch_processor.git

# Set the working directory
WORKDIR /sox_batch_processor
ENV SCRIPT_DIR /sox_batch_processor

RUN tar -xvf "$SCRIPT_DIR/libmad-0.15.1b.tar.gz" -C "$SCRIPT_DIR" \
&& cd libmad-0.15.1b \
&& ./configure --prefix="$SCRIPT_DIR/local" \
&& make clean \
&& make install

RUN tar -xvf "$SCRIPT_DIR/flac-1.4.3.tar.xz" -C "$SCRIPT_DIR" \
&& cd flac-1.4.3 \
&& ./configure --prefix="$SCRIPT_DIR/local" \
&& make clean \
&& make install

RUN tar -xvf "$SCRIPT_DIR/lame-3.99.5.tar.gz" -C "$SCRIPT_DIR" \
&& lame-3.99.5 \ 
&& ./configure --prefix="$SCRIPT_DIR/local" \
&& make clean \
&& make install


# Run setup.sh
RUN ./setup.sh


