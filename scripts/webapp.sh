#!/bin/sh

cd src/reviewer
uvicorn webapp.app:socket_app --timeout-keep-alive 600 

