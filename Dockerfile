FROM python:3.6

RUN apt-get update && apt-get install -y cmake
RUN wget https://github.com/libgit2/libgit2/archive/v0.27.0.tar.gz
RUN tar xzf v0.27.0.tar.gz
RUN cd libgit2-0.27.0 \
    && cmake . \
    && make \
    && make install

WORKDIR /usr/src/app

RUN pip install sphinx
RUN pip install sphinx_rtd_theme
RUN pip install tokenlib
RUN pip install cryptography
RUN pip install pygit2
RUN pip install django==1.11.3
RUN pip install coveralls
RUN pip install django-robots
RUN pip3 install django-cors-headers
RUN pip install coverage
RUN pip install coveralls
RUN pip install pyjwt
RUN pip install profilehooks
RUN pip install mixpanel
RUN pip install boto3
RUN pip install jose

RUN ldconfig

EXPOSE 8000
ENTRYPOINT ["python"]
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
