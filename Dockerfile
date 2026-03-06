FROM python:3.13-slim

WORKDIR /app/challenge_solution

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY challenge_solution/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY challenge_solution/ /app/challenge_solution/
COPY inputs/ /app/inputs/

EXPOSE 8000

CMD ["uvicorn", "web_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
