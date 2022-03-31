# Create our image based on Python 3.8
FROM python:3.8

# Expose ports
EXPOSE 5000

# Tell Python to not generate .pyc
ENV PYTHONDONTWRITEBYTECODE 1

# Turn off buffering
ENV PYTHONUNBUFFERED 1

# Add requirements file
ADD requirements.txt .

# Set working directory and addour Flask API files
WORKDIR /app
ADD . /app

# Anything added to the end of the docker run command
# is appended to the entrypoint command
ENTRYPOINT ["./entrypoint.sh"]