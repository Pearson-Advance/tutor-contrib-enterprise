import io
import os
import re
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Requirements will include any constraints from files specified
    with -c in the requirements files.
    Returns a list of requirement strings.
    """
    requirements = {}
    constraint_files = set()

    # groups "pkg<=x.y.z,..." into ("pkg", "<=x.y.z,...")
    requirement_line_regex = re.compile(r"([a-zA-Z0-9-_.]+)([<>=][^#\s]+)?")

    def add_version_constraint_or_raise(current_line, current_requirements, add_if_not_present):
        regex_match = requirement_line_regex.match(current_line)
        if regex_match:
            package = regex_match.group(1)
            version_constraints = regex_match.group(2)
            existing_version_constraints = current_requirements.get(package, None)
            # fine to add constraints to an unconstrained package,
            # raise an error if there are already constraints in place
            if existing_version_constraints and existing_version_constraints != version_constraints:
                raise BaseException(  # pylint: disable=broad-exception-raised
                    f'Multiple constraint definitions found for {package}:'
                    f' "{existing_version_constraints}" and "{version_constraints}".'
                    f'Combine constraints into one location with {package}'
                    f'{existing_version_constraints},{version_constraints}.',
                )
            if add_if_not_present or package in current_requirements:
                current_requirements[package] = version_constraints

    # read requirements from .in
    # store the path to any constraint files that are pulled in
    for path in requirements_paths:
        with open(path, encoding='utf-8') as reqs:
            for line in reqs:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, True)
                if line and line.startswith('-c') and not line.startswith('-c http'):
                    constraint_files.add(os.path.dirname(path) + '/' + line.split('#')[0].replace('-c', '').strip())

    # process constraint files: add constraints to existing requirements
    for constraint_file in constraint_files:
        with open(constraint_file, encoding='utf-8') as reader:
            for line in reader:
                if is_requirement(line):
                    add_version_constraint_or_raise(line, requirements, False)

    # process back into list of pkg><=constraints strings
    constrained_requirements = [f'{pkg}{version or ""}' for (pkg, version) in sorted(requirements.items())]
    return constrained_requirements


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment,
        a URL, or an included file
    """
    return line and line.strip() and not line.startswith(("-r", "#", "-e", "git+", "-c"))


def load_readme():
    with io.open(os.path.join(HERE, "README.md"), "rt", encoding="utf8") as f:
        return f.read()


def load_about():
    about = {}
    with io.open(
        os.path.join(HERE, "tutorenterprise", "__about__.py"),
        "rt",
        encoding="utf-8",
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about


ABOUT = load_about()


setup(
    name="tutor-contrib-enterprise",
    version=ABOUT["__version__"],
    url="https://github.com/Pearson-Advance/tutor-contrib-enterprise",
    project_urls={
        "Code": "https://github.com/Pearson-Advance/tutor-contrib-enterprise",
        "Issue tracker": "https://github.com/Pearson-Advance/tutor-contrib-enterprise/issues",
    },
    license="Apache-2.0",
    author="eduNEXT <contact@edunext.co>",
    description="Open edX Enterprise plugin for Tutor",
    long_description=load_readme(),
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=load_requirements('requirements/base.in'),
    entry_points={
        "tutor.plugin.v1": [
            "enterprise = tutorenterprise.plugin"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: 'Apache License Version 2.0'",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
