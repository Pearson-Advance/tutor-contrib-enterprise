# tutor-contrib-enterprise

This plugin allows to use [Enterprise](https://github.com/openedx/edx-enterprise) and [Enterprise Catalogue](https://github.com/openedx/enterprise-catalog) service in a Tutor-based installation.

## Support

edx-platform version: Olive
Tutor: 15.x.x

## Installation

    pip install git+https://github.com/Pearson-Advance/tutor-contrib-enterprise

## Usage

    tutor plugins enable enterprise

## Getting started.

Before enabling this plugin, you must install and enable the following plugins:
- [Tutor-ecommerce](https://github.com/overhangio/tutor-ecommerce)
- [Tutor-discovery](https://github.com/overhangio/tutor-discovery)
- [Tutor-mfe](https://github.com/overhangio/tutor-mfe)

Enterprise uses the Discovery APIs to obtain information about courses, so every time you make a change to a course or create a new course,
you will need to reindex the data in Discovery: https://github.com/overhangio/tutor-discovery#re-indexing-courses
otherwise, Enterprise enrollments will fail.

## Enterprise Catalogue service.

### Getting started.

This Tutor plugin will setup the Enterprise Catalogue IDA: https://github.com/openedx/enterprise-catalog

If you are provisioning a new Tutor installation, you will probably run: `tutor local launch`, this will set up the Enterprise Catalogue IDA along with your Open edX installation. If you have already run: `tutor local launch`, you will need to install and enable this tutor plugin and then run: `tutor local do init --limit=enterprise`, this will run all initialization tasks for the Enterprise Catalog IDA to work correctly. Finally run: `tutor local restart`.

### Create superuser:

In order to access the Enterprise Catalogue service as an admin user, you will need to first go to: http://enterprise-catalog.local.overhang.io/login with your Open edX super user. You should be redirected to the LMS login page in case you were not logged in. Then this user must be made a staff/superuser in enterprise-catalog service:

`tutor local run enterprise-catalog ./manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.filter(email='USER@EMAIL.COM').update(is_staff=True, is_superuser=True)"`

Replace the email parameter with your Open edX super user.

### Sync data:

To use the Enterprise Catalog service correctly, you will need to migrate existing enterprise catalogs stored in the LMS to the Enterprise Catalog service. This service also needs metadata related to the courses, so to do this, you need to run a command to synchronize the data between the Enterprise Catalog service and Discovery. To create the data and synchronize the course data, run the following command:

`tutor local do sync-enterprise-catalog-metadata`

Make sure that Discovery has up-to-date course data, otherwise Enterprise Catalogue service will create outdated course content metadata. To update Discovery course metadata, you can use: https://edx-discovery.readthedocs.io/en/latest/quickstart.html#data-loaders. It's also necessary to update Elastic Search index in Discovery: https://edx-discovery.readthedocs.io/en/latest/quickstart.html#search-indexing

### Troubleshooting:

Sometimes course content metadata is not created after running: `sync-enterprise-catalog-metadata`, this could happen if:

1. There is no Enterprise catalog query that meets the criteria of the courses you want to syncronize.
2. Courses and course runs in Discovery don't have a course type assigned. In this case you need to manually assign the course type
and re-index Elastic Search data in Discovery: https://edx-discovery.readthedocs.io/en/latest/quickstart.html#search-indexing
