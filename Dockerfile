# Create our image based on Python 3.8
FROM python:3.8

# Expose ports
EXPOSE 5000

# Tell Python to not generate .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Turn off buffering
ENV PYTHONUNBUFFERED 1

ARG MONGODB_USERNAME
ENV MONGODB_USERNAME $MONGODB_USERNAME

ARG MONGODB_PASSWORD
ENV MONGODB_PASSWORD $MONGODB_PASSWORD

ARG MONGODB_HOST
ENV MONGODB_HOST $MONGODB_HOST

# Install requirements using pip
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

# Set working directory and addour Flask API files
WORKDIR /app
ADD . /app

# RUN python /app/db_scripts/create_api_user.py admin password
