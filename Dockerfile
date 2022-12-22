FROM nvidia/cuda:12.0.0-base-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NOWARNINGS="yes"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# mdkir & cd
WORKDIR /app

COPY . . 

ENV PATH /opt/conda/bin:$PATH

# Install Dependencies of Miniconda
RUN apt-get update --fix-missing && \
    apt-get install -y ffmpeg wget bzip2 curl git mpv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate my_env" >> ~/.bashrc

RUN /bin/bash -c "conda create -n my_env"
    
RUN /bin/bash -c "source activate my_env" 

RUN conda update -n base -c defaults conda

RUN conda install numpy ipython pip matplotlib
RUN conda clean -a

RUN pip install opencv-python pyqt5 mediapipe --no-cache-dir

# recommended way:
# RUN pip install --no-cach-dir -r requirements.txt

CMD [ "/bin/bash" ]