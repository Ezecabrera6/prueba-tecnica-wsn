FROM python:3.13-slim

WORKDIR /app/challenge_solution

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY challenge_solution/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY challenge_solution/ /app/challenge_solution/
COPY inputs/ /app/inputs/
