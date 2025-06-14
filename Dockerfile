FROM python:3.12-slim

# this needs to match the directory/package name of the python app
# TODO: Copy only specific needed files and folders across
COPY . /apiserver
WORKDIR /apiserver

RUN rm -f .coverage && \
    rm -rf .git/ && \
    rm -rf apiserver/tests && \
    rm -rf dispatcher/tests && \
    rm -rf htmlcov && \
    rm -rf vapi && \
    rm -f docker-compose.yml && \
    rm -f .DS_Store && \
    rm -rf .idea && \
    rm -f poptape_apiserver.log && \
    rm -f apiserver.log && \
    mkdir -p /apiserver/log

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip  && \
    pip install --trusted-host pypi.python.org -r requirements.txt

# if -u flag in CMD below doesn't work
# then uncomment this to see python
# print statements in docker logs
ENV PYTHONUNBUFFERED=0

# run gunicorn
#CMD ["gunicorn", "-b", "0.0.0.0:9100", "auctionhouse.wsgi:application"]
#CMD ["python", "manage.py", "process_tasks"]

# Run start script for background tasks
CMD ["./run_app.sh"]
#RUN ["python", "manage.py", "process_tasks"]

# Make port 9500 available to the world outside this container
EXPOSE 9500
