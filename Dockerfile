FROM python:3.10.16

# Create vscode user with sudo
RUN useradd -m vscode && \
    echo "vscode:vscode" | chpasswd && \
    usermod -aG sudo vscode

# Set workdir and environment
WORKDIR /usr/src/app
ENV PATH /home/vscode/.local/bin:${PATH}
ENV KUBECONFIG=/home/vscode/.kube/config

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    curl \
    libpq-dev \
    gnupg \
    python3-pip \
    netcat-openbsd \
    && apt-get clean

# Install kubectl
RUN bash -c '\
    set -e; \
    KUBECTL_VERSION=$(curl -sSL https://dl.k8s.io/release/stable.txt); \
    echo "Installing kubectl version $KUBECTL_VERSION"; \
    curl -LO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"; \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl; \
    rm kubectl'



# Switch to vscode user
USER vscode
RUN mkdir -p /home/vscode/.kube

# Install Python packages
RUN pip install --upgrade pip wheel ansible
COPY requirements.txt.old .
RUN pip install -r requirements.txt.old

# Copy project files
COPY . .

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000"]
