Getting Started
===============

This guide will help you get started with Astra for automating your observatory.

Basic Concepts
-------------

Astra (Automated Survey observaTory Robotised with Alpaca) is a Python library designed to automate astronomical observations using the ASCOM Alpaca protocol. It provides a framework for controlling observatory equipment, scheduling observations, and processing data.

Key components of the Astra system:

1. **Observatory**: Central management of all observatory operations
2. **Devices**: ASCOM Alpaca-compatible astronomy equipment (telescopes, cameras, domes, etc.)
3. **Scheduling**: Planning and executing observation sequences
4. **Image processing**: Capturing, storing, and processing astronomical images

Configuration
------------

Before using Astra, you need to create configuration files for your observatory. These files define the equipment, preferences, and settings used by Astra.

Basic configuration structure:

1. Create an observatory configuration file (e.g., ``my_observatory_config.yaml``) in the ``config`` directory
2. Define your devices (telescopes, cameras, filter wheels, etc.)
3. Set up FITS header configuration in ``config/<observatory-name>_fits_headers.csv``
4. Create a schedule file in ``schedule/<observatory-name>.csv``

Example Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # Basic observatory configuration
    Misc:
      backup_time: "03:00"  # Daily backup time
    
    # Define telescope
    Telescope:
      - device_name: "Main Telescope"
        device_type: "Telescope"
        device_number: 0
        address: "localhost:11111"
        pointing_threshold: 30  # arcseconds
        
        # Guider configuration
        guider:
          guiding_interval: 10  # seconds
          guiding_max_correction: 5  # arcseconds
    
    # Define camera
    Camera:
      - device_name: "Main Camera"
        device_type: "Camera"
        device_number: 0
        address: "localhost:11112"
        temperature: -20  # target cooling temperature
        temperature_tolerance: 1
        
        # Paired devices to use with this camera
        paired_devices:
          Telescope: "Main Telescope"
          FilterWheel: "Filter Wheel"
          Focuser: "Main Focuser"
        
        # Flats configuration
        flats:
          target_adu: 30000
          bias_offset: 1000
          lower_exptime_limit: 0.1
          upper_exptime_limit: 15
    
    # Define filter wheel
    FilterWheel:
      - device_name: "Filter Wheel"
        device_type: "FilterWheel"
        device_number: 0
        address: "localhost:11113"

Running Astra
------------

Once configured, you can start Astra:

1. Ensure your ASCOM Alpaca devices or simulators are running on your network
2. Run the command:

   .. code-block:: bash

       python src/astra/main.py

3. Follow the terminal instructions
4. Access the web interface at http://localhost:8000/

Creating a Schedule
-----------------

Observations are controlled by a schedule CSV file. The schedule defines what actions to perform and when to perform them.

Example schedule structure:

.. code-block:: text

    device_type,device_name,action_type,action_value,start_time,end_time
    Camera,Main Camera,open,"{}",2025-04-14T20:00:00,2025-04-14T20:05:00
    Camera,Main Camera,autofocus,"{'exptime': 3, 'filter': 'R'}",2025-04-14T20:05:00,2025-04-14T20:30:00
    Camera,Main Camera,object,"{'object': 'M51', 'ra': 202.48, 'dec': 47.195, 'exptime': 120, 'n': 10, 'filter': 'R', 'guiding': true, 'pointing': true}",2025-04-14T20:30:00,2025-04-14T22:30:00
    Camera,Main Camera,close,"{}",2025-04-14T22:30:00,2025-04-14T22:35:00
    
Save this as a CSV file in the ``schedule`` directory (e.g., ``schedule/my_observatory.csv``) and Astra will automatically detect and execute it according to the specified times.

Next Steps
---------

* Learn more about :doc:`observatory configuration <user_guide/configuration>`
* Explore advanced :doc:`scheduling options <user_guide/scheduling>`
* Read about :doc:`autoguiding <user_guide/guiding>` and :doc:`autofocus <user_guide/autofocus>`