FROM python:3.9.7 as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc

COPY . .

USER root

RUN pip install --upgrade pip && \
    pip install --no-cache -r requirements.txt

RUN python src/process.py

FROM python:3.9.7-slim

WORKDIR /app

COPY src/app.py .
COPY --from=builder /app/db-final-ratings.csv .
COPY --from=builder /app/model.pkl .
COPY --from=builder /app/requirements.txt .

USER root

RUN pip install --upgrade pip && \
    pip install --no-cache -r requirements.txt


ENTRYPOINT [ "python", "app.py" ]