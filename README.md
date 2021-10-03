# PSONO Fileserver - Password Manager

Master:  [![build status](https://gitlab.com/psono/psono-fileserver/badges/master/pipeline.svg)](https://gitlab.com/psono/psono-fileserver/commits/master) [![coverage report](https://gitlab.com/psono/psono-fileserver/badges/master/coverage.svg)](https://gitlab.com/psono/psono-fileserver/commits/master) [![Code Climate](https://codeclimate.com/github/psono/psono-fileserver/badges/gpa.svg)](https://codeclimate.com/github/psono/psono-fileserver) [![build status](https://img.shields.io/docker/pulls/psono/psono-fileserver.svg)](https://hub.docker.com/r/psono/psono-fileserver/)

Develop: [![build status](https://gitlab.com/psono/psono-fileserver/badges/develop/pipeline.svg)](https://gitlab.com/psono/psono-fileserver/commits/develop) [![coverage report](https://gitlab.com/psono/psono-fileserver/badges/develop/coverage.svg)](https://gitlab.com/psono/psono-fileserver/commits/develop)

# Canonical source

The canonical source of PSONO Fileserver is [hosted on GitLab.com](https://gitlab.com/psono/psono-fileserver).

# Documentation

The documentation for the psono fileserver can be found here:

[Psono Documentation](https://doc.psono.com/)

Some things that have not yet found their place in the documentation:

## Storage Engines:

Psono Fileserver is using "django-storages" as storage engine. The official documentation for django-storages can be found here:
http://django-storages.readthedocs.io/en/latest/index.html

Supported Provider are:

* Amazon S3
* Apache Libcloud
* Azure Storage
* Digital Ocean
* DropBox
* FTP
* Google Cloud Storage
* SFTP

storages.backends.s3boto3.S3Boto3Storage


## LICENSE

Visit the [License.md](/LICENSE.md) for more details
