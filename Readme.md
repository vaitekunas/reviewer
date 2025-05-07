# Customer Review Analytics

## Startup

```shell
cd src/reviewer
uvicorn webapp.app:socket_app --timeout-keep-alive 6000 
```

To start the application in development mode:
```
cd src/reviewer/webapp
ENV=dev uvicorn webapp.app:socket_app --timeout-keep-alive 6000 --reload
```

Icons: [Untitled UI](https://www.untitledui.com/free-icons)
