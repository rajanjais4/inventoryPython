From python:3.9
WORKDIR ./inventoryPyApp
COPY ./requirement.txt  .
RUN pip install -r requirement.txt
COPY ./src ./src
CMD ["python", "./src/server.py"]