# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload", "--reload-dir", "/code/app"]
#RUN curl --request POST -H "Content-Type: application/json" --data '{"email":"admin@admin.com","password":"123"}' http://127.0.0.1/users

