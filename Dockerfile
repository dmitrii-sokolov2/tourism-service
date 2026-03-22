FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
<<<<<<< HEAD
RUN pip install --no-cache-dir -r requirements.txt
=======
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
>>>>>>> api-refactor

COPY . .

CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]