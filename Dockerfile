FROM python:3
RUN mkdir /vk-filter
WORKDIR /vk-filter
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /vk-filter
RUN mkdir -p /var/www/vk-filter