# Welder 

## Installation Requirements

* [Python 3](http://python-guide-pt-br.readthedocs.io/en/latest/starting/installation/) - Requires python 3.6 or newer.
* [Git](https://git-scm.com/downloads) - Latest version.
* [libgit2](https://github.com/libgit2/libgit2) - Latest version. Libgit2 is a portable, pure C implementation of the Git core methods.

## Usage

Install local requirements:

```
$ pip install -r requirements.txt
```

Run the server:
```
$ python manage.py runserver
```

### Running with Docker

Build a container using the Dockerfile in the root directory

```
docker build -t welder .
```

Run the container as part of a composition

```
...

  welder:
    command: python manage.py runserver [::]:9000
    image: btcrs/welder
    volumes:
      - ../../Welder/:/app
    working_dir: /app
    networks:
      - net
    ports:
      - "9000:9000"

networks:
  net:
```


## Examples
In all examples api is the base url, user and project can be whatever you choose. Username and password are not enforced.

Creating  repo:

```
 curl -X POST \
  {{api}}/{{user}}/{{project}}/create \
  -H "Content-Type: application/json"
```

Cloning a repo. In the command line:

```
 $ git clone {{project}}
```

## Maintainers

[@wevolver](https://github.com/wevolver)

## License
© 2017 Wevolver
