Installation
============

``vcon`` requires Python 3.12 or later.

Using pip
---------

.. code-block:: bash

    pip install vcon

The image and PDF helpers need Pillow and pypdf, which the ``image`` extra
installs:

.. code-block:: bash

    pip install "vcon[image]"

The video helpers (metadata, thumbnails, transcoding) need ffmpeg-python,
which the ``video`` extra installs, and the ``ffmpeg`` binary on your
``PATH``:

.. code-block:: bash

    pip install "vcon[video]"

From source
-----------

The project uses Poetry:

.. code-block:: bash

    git clone https://github.com/vcon-dev/vcon-lib.git
    cd vcon-lib
    poetry install
    poetry run pytest

To build these docs locally:

.. code-block:: bash

    poetry install --with dev
    cd docs
    poetry run make html

The output is in ``docs/build/html``.

Dependencies
------------

The runtime dependencies are listed in ``pyproject.toml`` and installed
automatically: joserfc (JWS signing), uuid6, requests, pydash,
python-dateutil and mutagen. Pillow and pypdf come with the ``image`` extra,
ffmpeg-python with the ``video`` extra.
