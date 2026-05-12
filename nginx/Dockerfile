FROM node:18 AS frontend-build

WORKDIR /frontend

COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend .

RUN npm run build


FROM nginx:alpine

COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=frontend-build /frontend/dist /usr/share/nginx/html