## From build start here step 1

From python:3.14-slim

## Step 2 path for the folder

WORKDIR /app

## REQUIREMNET.txt 

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt


## Step 4 BUild for th file in container

COPY . .

## Port we will run the file

Expose 5000

## last usage of run

CMD ["python","app.py"]

