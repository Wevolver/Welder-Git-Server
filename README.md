# Welder 

[![Build Status](https://travis-ci.org/Wevolver/Welder.svg?branch=master)](https://travis-ci.org/Wevolver/Welder) [![API Docs](https://img.shields.io/badge/API-Slate-ff69b4.svg)](https://wevolver.github.io/WelderApi/#introduction)

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

<!--## Contributing

The main purpose of this repository is to continue to evolve Groot, making it faster, more powerful and easier to use.

### Code of Conduct

Wevolver has adopted a Code of Conduct that we expect project participants to adhere to. Please read the full text so that you can understand what actions will and will not be tolerated.

### Contributing Guide

Read our contributing guide to learn about our development process, how to propose bugfixes and improvements, and how to build and test your changes to React.


### Beginer friendly features and bugs

To help you get your feet wet and get you familiar with our contribution process, we have a list of beginner friendly bugs that contain bugs which are fairly easy to fix. This is a great place to get started.-->

## Maintainers

[@wevolver](https://github.com/wevolver)

## License
© 2017 Wevolver
