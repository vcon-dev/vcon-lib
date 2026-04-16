Installation
============

There are several ways to install the vcon library.

Using pip
---------

The simplest way to install vcon is using pip:

.. code-block:: bash

    pip install vcon

Using Poetry (recommended for development)
------------------------------------------

For development, we recommend using Poetry:

1. First, install Poetry if you haven't already:

   .. code-block:: bash

       curl -sSL https://install.python-poetry.org | python3 -

2. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/vcon-dev/vcon-lib.git
       cd vcon-lib

3. Install dependencies:

   .. code-block:: bash

       poetry install

This will create a virtual environment and install all dependencies, including development dependencies.

Requirements
------------

vcon requires Python 3.12 or later and has the following main dependencies:

- authlib>=1.6.4
- uuid6>=2024.7.10
- requests>=2.32.3
- pydash>=8.0.3
- python-dateutil>=2.9.0
- mutagen>=1.47.0
- ffmpeg>=1.4
- logger>=1.4
- pypdf>=6.0.0
- pillow>=11.3.0

Some video processing features require the `ffmpeg` system binary to be installed and available on your PATH.

These dependencies will be automatically installed when you install vcon using any of the methods above. 
