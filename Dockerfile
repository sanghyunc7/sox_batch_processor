# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04


# Update package lists and install git
RUN apt-get update && apt-get install -y git
# only for docker
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

# Clone the repository
RUN git clone https://github.com/sanghyunc7/sox_batch_processor.git

# Set the working directory
WORKDIR /sox_batch_processor

# Run setup.sh
RUN ./setup.sh

# Run sox
CMD ["sox"]
