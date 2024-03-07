

template:
```bash
scalene  {file_path}   --reduced-profile --html --outfile ./{result}.html  --use-virtual-time 
```

1. web-demo scalene test

```bash
scalene  /home/atticuszz/DevSpace/python/BoostFace/src/Demo/web/main.py  --reduced-profile --html --outfile ./web_demo.html  --use-virtual-time  
```


# 2. backend-demo scalene test

```bash
scalene  /home/atticuszz/DevSpace/python/BoostFace/src/Demo/backend/main.py   --html --outfile ./backend.html --reduced-profile  --use-virtual-time
```


scalene  /home/atticuszz/DevSpace/python/BoostFace/tests/scalene_test.py  --html --outfile ./test.html --reduced-profile --cpu-percent-threshold 0.1 --memory-leak-detector --profile-all

