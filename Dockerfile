FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN cd protos && python -m grpc_tools.protoc -I. --python_out=../ --grpc_python_out=../ index.proto
ENV PYTHONUNBUFFERED=1
