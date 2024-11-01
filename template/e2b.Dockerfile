FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_PRIORITY=high

RUN yes | unminimize

RUN apt-get update && apt-get install -y \
  python3-xlib \
  x11-xserver-utils \
  xfce4 \
  xfce4-goodies \
  xvfb \
  xubuntu-icon-theme \
  scrot \
  python3-pip \
  python3-tk \
  python3-dev \
  x11-utils \
  gnumeric \
  python-is-python3 \
  build-essential \
  util-linux \
  locales \
  xauth \
  gnome-screenshot \
  xserver-xorg \
  ffmpeg \
  vim \
  xorg

RUN pip3 install mux_python requests

# Install vscode
RUN apt update -y \
  && apt install -y software-properties-common apt-transport-https wget \
  && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && add-apt-repository -y "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" \
  && apt update -y \
  && apt install -y code

ENV PIP_DEFAULT_TIMEOUT=100 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1 \
  DEBIAN_FRONTEND=noninteractive

RUN echo "export DISPLAY=:99" >> /etc/environment

COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./45-allow-colord.pkla /etc/polkit-1/localauthority/50-local.d/45-allow-colord.pkla

COPY ./Xauthority /home/user/.Xauthority

COPY ./start-up.sh /
RUN chmod +x /start-up.sh

RUN apt-get update && \
  apt-get -y upgrade && \
  apt-get -y install \
  build-essential \
  # UI Requirements
  xvfb \
  xterm \
  xdotool \
  scrot \
  imagemagick \
  sudo \
  mutter \
  x11vnc \
  # Python/pyenv reqs
  build-essential \
  libssl-dev  \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  curl \
  git \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libxml2-dev \
  libxmlsec1-dev \
  libffi-dev \
  liblzma-dev \
  # Network tools
  net-tools \
  netcat \
  # PPA req
  software-properties-common && \
  # Userland apps
  sudo add-apt-repository ppa:mozillateam/ppa && \
  sudo apt-get install -y --no-install-recommends \
  libreoffice \
  firefox-esr \
  x11-apps \
  xpdf \
  gedit \
  xpaint \
  tint2 \
  galculator \
  pcmanfm \
  unzip && \
  apt-get clean