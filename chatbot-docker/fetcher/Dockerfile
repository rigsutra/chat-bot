FROM python:3.11-slim

WORKDIR /fetcher

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fetcher.py .

CMD ["python", "fetcher.py"]