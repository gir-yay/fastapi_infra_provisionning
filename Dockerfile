FROM python:3.10
RUN useradd -m vscode && \
    echo "vscode:vscode" | chpasswd && \
    usermod -aG sudo vscode

# Set vscode as the default user
USER vscode
WORKDIR /usr/src/app
ENV PATH /home/vscode/.local/bin:${PATH}
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install fastapi[all]
RUN pip install pydantic-settings
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000", "--reload"]