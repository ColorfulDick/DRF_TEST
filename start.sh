#!/bin/bash

#命令只执行最后一个,所以用 &&

python3 manage.py collectstatic --noinput &&
python3 manage.py migrate &&
#gunicorn Mydrf.asgi:application -D -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 以后台进程运行gunicorn(加入-D参数)
gunicorn Mydrf.asgi:application -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 #在docker中必须以前台进程来运行gunicorn，不然docker会认为容器已经挂掉

#在源文件更改，镜像内的也会随之改变
