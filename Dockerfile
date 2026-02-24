FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dungeon_game.py dungeon_ascii_art.py server.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python3", "server.py"]
