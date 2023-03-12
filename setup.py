import setuptools
from source import VERSION_PROGRAM, NAME

ignored_dependencies = []


def get_dependencies():
    with open("requirements.txt", "r") as fh:
        requirements = fh.read()
        requirements = requirements.split('\n')
        map(lambda r: r.strip(), requirements)
        requirements = [r for r in requirements if r not in ignored_dependencies]
        return requirements


setuptools.setup(
    name=NAME,
    version=VERSION_PROGRAM,
    entry_points={
        'console_scripts': [
            'pirate_audio_plugin=source.main:main',
        ],
    },
    author="AX-LED & Valentin Rudloff",
    author_email="valentin.rudloff.perso@gmail.com",
    description="This is the Volumio plugin for the Pirate Audio HAT for Raspberry Pi.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    include_package_data=True,
    install_requires=get_dependencies()
)
