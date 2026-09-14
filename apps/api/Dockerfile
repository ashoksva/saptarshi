FROM python:3.12-slim

WORKDIR /srv
COPY packages/agents /srv/packages/agents
COPY apps/api /srv/apps/api
ENV PYTHONPATH=/srv/packages/agents:/srv/apps/api
RUN pip install --no-cache-dir -r /srv/apps/api/requirements.txt

WORKDIR /srv/apps/api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
