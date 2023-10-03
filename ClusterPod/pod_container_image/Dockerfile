FROM python:3.10

RUN apt-get update && apt-get install -y \
    unzip \
    vim

WORKDIR /home
CMD ["mkdir", "output"]

COPY . .

RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install