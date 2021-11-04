# sessiyabot/Dockerfile
# -docker container settings
# Config file needs to add MANUALLY
# Marakulin Andrey @annndruha
# 2019

# Base image
FROM python:3.7.6-stretch

# Create directoris inside container
ADD ./ /sessiyabot
WORKDIR /sessiyabot

# Install libs from requirements
RUN pip install --no-cache-dir -r requirements.txt

# Specify the port number the container should expose 
EXPOSE 42

# Run the file
CMD ["python", "-u", "./sessiyabot.py"]

# Example docker Ubuntu command:
# docker run -d --name sessiyabot -v /root/sessiyabot/configvolume.py:/sessiyabot/data/config.py imagename

# See logs:
# docker logs sessiyabot --follow