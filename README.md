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
