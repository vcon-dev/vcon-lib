Usage Guide
===========

This guide will help you get started with using the vcon library.

Basic Usage
----------

Creating a vCon Container
~~~~~~~~~~~~~~~~~~~~~~~

Here's a simple example of creating a vCon container:

.. code-block:: python

    from vcon import VCon
    
    # Create a new vCon container
    vcon = VCon()
    
    # Set basic metadata
    vcon.set_title("My Video Conference")
    vcon.set_description("An important meeting")
    
    # Add participants
    vcon.add_participant(name="John Doe", email="john@example.com")
    
    # Save the container
    vcon.save("my_conference.vcon")

Reading a vCon Container
~~~~~~~~~~~~~~~~~~~~~~~

To read an existing vCon container:

.. code-block:: python

    from vcon import VCon
    
    # Load a vCon container
    vcon = VCon.load("my_conference.vcon")
    
    # Access metadata
    title = vcon.get_title()
    description = vcon.get_description()
    
    # Get participants
    participants = vcon.get_participants()

Advanced Usage
-------------

Working with Media Files
~~~~~~~~~~~~~~~~~~~~~~~

You can attach and manage media files in a vCon container:

.. code-block:: python

    from vcon import VCon
    
    vcon = VCon()
    
    # Add a video recording
    vcon.add_media("recording.mp4", media_type="video/mp4")
    
    # Add a transcript
    vcon.add_media("transcript.txt", media_type="text/plain")

.. _api-reference:

API Reference
------------

For more detailed information about the API, please refer to the sections below. 