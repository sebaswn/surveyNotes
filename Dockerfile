FROM node:12 AS build
RUN apt-get update && apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update && apt-get install -y nodejs



WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
RUN npm install
COPY . ./
WORKDIR /client
RUN npm run build

FROM nginx:1.19-alpine
COPY --from=build /app/public /usr/share/nginx/html



# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["test.py" ]