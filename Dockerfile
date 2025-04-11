FROM python:3.10.16
RUN useradd -m vscode && \
    echo "vscode:vscode" | chpasswd && \
    usermod -aG sudo vscode

USER root
RUN apt-get update && apt-get install -y 
RUN apt-get install -y libpq-dev
RUN apt-get install -y python3-pip


# Set vscode as the default user
USER vscode
WORKDIR /usr/src/app
ENV PATH /home/vscode/.local/bin:${PATH}
RUN pip install --upgrade pip
RUN pip install wheel


COPY requirements.txt.old .
RUN pip install -r requirements.txt.old


COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000"]