from __future__ import annotations

import os
import os.path
import typing as t
from glob import glob

import click
import pkg_resources
from tutor import hooks

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

config = {
    "defaults": {
        "VERSION": __version__,
        "OAUTH2_KEY": "enterprise-backend-service",
        "WORKER_USER_NAME": "enterprise_worker",
        "WORKER_USER_EMAIL": "enterprise_worker@example.com",
        "COURSE_CATALOG_API_URL": "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ DISCOVERY_HOST }}/api/v1/",
        "CATALOG_REPOSITORY": "https://github.com/Pearson-Advance/enterprise-catalog.git",
        "CATALOG_GIT_VERSION": "open-release/pre-quince",
        "CATALOG_WORKER_USER_NAME": "enterprise_catalog_worker",
        "CATALOG_WORKER_USER_EMAIL": "enterprise_catalog_worker@example.com",
        "CATALOG_HOST": "enterprise-catalog.{{ LMS_HOST }}",
        "CATALOG_OAUTH2_KEY_SSO": "enterprise_catalog-sso-key",
        "CATALOG_OAUTH2_KEY": "enterprise_catalog-backend-service",
        "CATALOG_MYSQL_DATABASE": "enterprise_catalog",
        "CATALOG_MYSQL_USERNAME": "enterprise_catalog",
        "CATALOG_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}paops/enterprise-catalog:{{ ENTERPRISE_VERSION }}",
        "DISCOVERY_USER": "discovery",
        "ECOMMERCE_OAUTH_USER": "{{ ECOMMERCE_OAUTH2_KEY }}",
    },
    "unique": {
        "OAUTH2_SECRET_KEY": "{{ 64|random_string }}",
        "CATALOG_SECRET_KEY": "{{ 20|random_string }}",
        "CATALOG_OAUTH2_SECRET_KEY_SSO": "{{ 64|random_string }}",
        "CATALOG_OAUTH2_SECRET_KEY": "{{ 64|random_string }}",
        "CATALOG_MYSQL_PASSWORD": "{{ 16|random_string }}",
    },
}

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"ENTERPRISE_{key}", value) for key, value in config.get("defaults", {}).items()],
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"ENTERPRISE_{key}", value) for key, value in config.get("unique", {}).items()],
)
hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config.get("overrides", {}).items()),
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutorenterprise/templates/enterprise/jobs/init/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutorenterprise/templates/enterprise/jobs/init/lms.sh
    # And then add the line:
    ### ("lms", ("enterprise", "jobs", "init", "lms.sh")),
    ("lms", ("enterprise", "jobs", "lms", "init")),
    ("mysql", ("enterprise", "jobs", "mysql", "init")),
    ("ecommerce", ("enterprise", "jobs", "ecommerce", "init")),
    ("discovery", ("enterprise", "jobs", "discovery", "init")),
    ("enterprise-catalog", ("enterprise", "jobs", "enterprise-catalog", "init")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = pkg_resources.resource_filename(
        "tutorenterprise", os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/enterprise/build/myimage,
        # and then write:
        ### (
        ###     "myimage",
        ###     ("plugins", "enterprise", "build", "myimage"),
        ###     "docker.io/myimage:{{ ENTERPRISE_VERSION }}",
        ###     (),
        ### ),
    ]
)


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ ENTERPRISE_VERSION }}",
        ### ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ ENTERPRISE_VERSION }}",
        ### ),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        pkg_resources.resource_filename("tutorenterprise", "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutorenterprise/templates/enterprise/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/enterprise/build``.
    [
        ("enterprise/build", "plugins"),
        ("enterprise/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutorenterprise/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("tutorenterprise", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################


# A job is a set of tasks, each of which run inside a certain container.
# Jobs are invoked using the `do` command, for example: `tutor local do importdemocourse`.
# A few jobs are built in to Tutor, such as `init` and `createuser`.
# You can also add your own custom jobs.
# To add a custom job, define a Click command that returns a list of tasks,
# where each task is a pair in the form ("<service>", "<shell_command>").
# For example:
@click.command()
def sync_enterprise_catalog_metadata() -> t.Iterable[tuple[str, str]]:
    """
    This command will sync the Enterprise Catalogue service data.

    Initially this command will migrate existing Enterprise Catalogues from the LMS
    to the Enterprise Catalogue service.
    Then, it will update the Enterprise catalogue content metadata, this will require data from
    Discovery service.
    """
    return [
        ("lms", enterprise_migrate_catalog_lms_task()),
        ("enterprise-catalog", enterprise_catalog_update_content_metadata_task()),
    ]


def enterprise_migrate_catalog_lms_task() -> str:
    """
    Return the instructions of the template: tutorenterprise/templates/enterprise/jobs/lms/migrate_catalogs
    """
    task_instructions = ""
    template_path = ("enterprise", "jobs", "lms", "migrate_catalogs")

    with open(
        return_template_full_path(template_path),
        encoding="utf-8",
    ) as lms_task_file:
        task_instructions: str = lms_task_file.read()

    return task_instructions


def enterprise_catalog_update_content_metadata_task() -> str:
    """
    Return the instructions of the template: tutorenterprise/templates/enterprise/jobs/enterprise-catalog/update_content_metadata
    """
    task_instructions = ""
    template_path = (
        "enterprise",
        "jobs",
        "enterprise-catalog",
        "update_content_metadata",
    )

    with open(
        return_template_full_path(template_path),
        encoding="utf-8",
    ) as catalog_task_file:
        task_instructions: str = catalog_task_file.read()

    return task_instructions


def return_template_full_path(template_path: tuple) -> str:
    """
    Given the relative template path, it will return the full path of the template.
    """
    return pkg_resources.resource_filename(
        "tutorenterprise",
        os.path.join("templates", *template_path),
    )


# Then, add the command function to CLI_DO_COMMANDS:
hooks.Filters.CLI_DO_COMMANDS.add_item(sync_enterprise_catalog_metadata)

# Now, you can run your job like this:
#   $ tutor local do sync-enterprise-catalog-metadata


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def enterprise() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(enterprise)


# Then, you would add subcommands directly to the Click group, for example:


### @enterprise.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor enterprise example-command
