#!/bin/bash

# SetupTool version to be installed
SETUPTOOL_VERSION="65.0.0"
PY_VERSION_RE='^3(\.[0-9]+)(\.[0-9])?$'

# Install dependencies
install_common_dependencies() {
  echo Installing common dependencies
  sudo apt-get install -y make curl wget libltdl7 libseccomp2 libffi-dev gawk apt-transport-https ca-certificates \
  curl gnupg gnupg-agent lsb-release software-properties-common sshpass pv

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  # Update local repositories
  echo Updating local repositories
  sudo apt-get update
}

# Install Pyenv
install_pyenv() {
  if command -v pyenv 1; then
      echo pyenv is already installed
    else
      echo Installing pyenv dependencies
      sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
      libbz2-dev libreadline-dev libsqlite3-dev llvm \
      libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
      echo Downloading pyenv
      curl https://pyenv.run | bash
      export PATH="$HOME/.pyenv/bin:$PATH" && eval "$(pyenv init --path)" \
      && echo -e 'export PATH="$HOME/.pyenv/bin:$PATH"\nif command -v pyenv 1>/dev/null 2>&1; then\n eval "$(pyenv init -)"\nfi' >> ~/.bashrc
    fi
}

# Install Python
install_python() {
  echo Start Python $PYTHON_VERSION installation
  pyenv install $PYTHON_VERSION
  pyenv global $PYTHON_VERSION
  echo Finish Python Installtion
}

# Upgrade Python if version is below than $PYTHON_VERSION
upgrade_python {
  PYTHON_VERSION=${1}
  if [ -z $PYTHON_VERSION ] || ! [[ $PYTHON_VERSION =~ $re ]]; then
    return
  fi
  if $(dpkg --compare-versions $(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))') "lt" $PYTHON_VERSION); then
    install_pyenv
    install_python
  fi
}

# Install setuptools
install_setuptools {
  IFS=' '
  v=`python3 -m pip  list | grep -i setuptools | { read _ v; echo $v; }`
  if $(dpkg --compare-versions $v "gt" $SETUPTOOL_VERSION); then
    python3 -m pip install setuptools==65.0.0
  fi
  unset IFS v
}


# Install Python Dependencies
install_python_dependencies() {
  echo Installing Python dependencies
  sudo apt-get install -y python3-distutils
  sudo apt-get install -y python3-pip
  python3 -m pip install -U pip
  install_setuptools
}

# Install ansible if not present
install_ansible() {
  if [ "`which ansible`" != ""  ]; then
    echo Ansible already installed, skipping.
  else
    echo Installing ansible
    python3 -m pip install --user ansible
  fi
}


# Install docker if not present
install_docker() {
  echo Enabling docker repository
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
  if [ "`which docker`" != ""  ]; then
    echo Docker already installed, skipping.
  else
    echo Installing docker
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  fi
}


main() {
  install_common_dependencies
  upgrade_python ${1}
  install_python_dependencies
  install_ansible
  install_docker
  # Ensure /usr/local/bin is in path
  export PATH=$PATH:/usr/local/bin
  echo Restarting shell
  exec $SHELL
}


# Entry point. START
main ${1}
