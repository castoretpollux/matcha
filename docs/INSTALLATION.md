# Pre-Requisites

Before you can use Matcha, you'll need to get it installed.
Those are the tools that you'll need :

- Linux (it may work on MacOS and Windows but we didn't test it)
- Python 3.10+
- PostgreSQL 12+ (Note that Matcha uses Django but only PostgreSQL database backend can be used as we need pgvector extension)
- Node 18+ (we use version 18.19)
- npm (compatible with chosen node version)

Note : for Node and npm, we strongly advice you to use [nvm](https://github.com/nvm-sh/nvm)

# Hardware requirements & CUDA

- NVidia Card & Cuda : Matcha use IA models intensively and even if some models can be used thru CPU, having a GPU will speed up dramatically answers

To install CUDA on your platform, please refer to [CUDA installation](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)

# Installation

## Install system packages

Those packages are dependencies of LangChain which is used by Matcha :

```
sudo apt update
sudo apt install libleptonica-dev tesseract-ocr libtesseract-dev libmagic-dev poppler-utils libreoffice pandoc tesseract-ocr-script-latn

# optionnal, you can install tesseract-ocr for your language, for instance :
sudo apt install tesseract-ocr-fra
```


## Create Python virtual envs 

Currently, Matcha will need two virtual envs :

- one for the "core" which is referred as **"matcha"** in the documentation
- one for the search application which is referred as **"searchapp"** (which is used to vectorise and index documents that can be searched afterwards)

Note : this may change in the future, as we are aiming to make Matcha work in one single virtualenv.

To create a virtualenv, you can refer to [this doc](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

For practicality, create env "matcha" and "searchapp" if you can :

```
pip install virtualenv # to install Python virtual env package
python -m venv /path/to/venv/matcha # Change /path/to/venv to a local directory
python -m venv /path/to/venv/search # Change /path/to/venv to a local directory
```


## Clone Matcha repository :

```
git clone https://github.com/castoretpollux/matcha.git
```
The directory in which this repository was cloned will be called matcha_root_dir in the next lines


## Install the matcha python packages requirements :

```
source /path/to/venv/matcha/bin/activate # Change /path/to/venv to a local directory
pip install -r requirements/requirements.txt
```
## Install the searchapp python packages requirements :

```
source /path/to/venv/searchapp/bin/activate # Change /path/to/venv to a local directory
pip install -r processes/searchapp/requirements.txt
```

## Install npm packages for the frontend

```
cd <matcha_root_dir>/frontend
npm i
```

## Install Redis

```
sudo apt-get update
sudo apt-get install redis
```

Note : Redis is used with Django-RQ to run tasks asynchronously

## Install Ollama

Follow the instructions at : https://ollama.com/download

By using a local Ollama instance and its API, every Ollama supported AI model can be used in Matcha

## Download some ollama models to use with Matcha :

```
ollama pull <model_name>
```

Sample config.yaml makes use of llama3, so it's a good idea to pull it ! 

```
ollama pull llama3
```

## Setup databases

### Install PostgreSQL :

On debian based distribution :
```
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Install pgvector

Matcha is using PostgreSQL pgvector extension to store documents and chunks vectors.

If you're a ubuntu 22 user, you can follow this guide :
[pgvector installation on Ubuntu 22](https://rocketee.rs/install-postgresql-pgvector-ubuntu-22)

For other OS and distrib, look at the offical pgvector doc :
[pgvector](https://github.com/pgvector/pgvector)

### Create databases

Matcha needs 2 databases, each using the pgvector extension :

- matcha
- searchapp 

\* Note that those databases can have differents names, you'll have to modify the config.yaml consequently

To create databases and enable pgvector extension, launch a psql shell with enough credential to create databases and extension

```
psql

# in psql shell :
create database matcha;
\c matcha;
create extension vector;

# let's do the same for searchapp :
create database searchapp;
\c searchapp;
create extension vector;
```

## Create a config.yaml and adapt it to your needs

We provide and config.yaml example in config.yaml.sample, copy it and adapt it
```
cp config.yaml.sample config.yaml
```


## Synchronize databases

## Create superuser for matcha

Matcha is using Django Web Framework.
It should have been already installed when you installed core requirements

You'll need to create a superuser :

```
cd <matcha_root_dir>
python manage.py createsuperuser
# you must answer the questions to create the django superuser that is also a Matcha superuser
```

# Verifying

We provide a develpement environment.
To start it, just launch :
```
cd <matcha_root_dir>
python launch.py dev
```

Then, go to : https://localhost:3000 and connect using your superuser username and password

# That's it!

That's it -- you can now move to [TERMINOLOGY](/docs/TERMINOLOGY.md)