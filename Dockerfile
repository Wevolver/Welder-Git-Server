FROM python:3.6

RUN apt-get update && apt-get install -y cmake
RUN wget https://github.com/libgit2/libgit2/archive/v0.26.0.tar.gz
RUN tar xzf v0.26.0.tar.gz
RUN cd libgit2-0.26.0 \
    && cmake . \
    && make \
    && make install

RUN git clone https://github.com/Wevolver/Welder
COPY . /git_code

RUN pip install sphinx
RUN pip install sphinx_rtd_theme
RUN pip install tokenlib
RUN pip install cryptography
RUN pip install pygit2
RUN pip install django
RUN pip install coveralls
RUN pip install django-robots
RUN pip3 install django-cors-headers
RUN pip install coverage
RUN pip install coveralls
RUN pip install pyjwt
RUN pip install profilehooks
RUN pip install mixpanel

RUN ldconfig
