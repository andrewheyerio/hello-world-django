#############
Hello, Django
#############

This repository contains a Django based backend service. This backend service provides an API for
`Hello, React <https://github.com/fullstackheyer/hello-react-admin/>`_.
Some features implemented in this service are;

* JWT Authentication
* API's using DRF
* Docker
* Redis
* Stripe
* Sending email
* Filtering cached
* Scoping

This project supports two methods of deployment.
Development on a local machine and deployment on AWS
CodePipeline.

Here are steps and some notes to get this project working locally
in a development environment.

1. Pull the repository on you local machine
2. `cd` into the directory
3. do `docker-compose --env-file .env up`

