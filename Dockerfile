FROM python:3.10.16
RUN useradd -m vscode && \
    echo "vscode:vscode" | chpasswd && \
    usermod -aG sudo vscode

# Set vscode as the default user
USER vscode
WORKDIR /usr/src/app
ENV PATH /home/vscode/.local/bin:${PATH}
RUN sudo apt update && apt install -y 
RUN sudo apt install -y libpq-dev
RUN pip install fastapi[all]
RUN pip install psycopg2
RUN pip install passlib[bcrypt]
RUN pip install python-jose[cryptography]
RUN pip pip install alembic
RUN pip install pydantic-settings

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0",  "--port", "8000"]