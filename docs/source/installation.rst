Installation
============

Prerequisites
------------

Before installing Astra, ensure you have the following prerequisites:

* Python 3.11 or higher
* ASCOM Platform (for Windows) or ASCOM Alpaca-compatible devices
* Git (for installation from source)

Installation Steps
-----------------

1. Clone the Astra repository:

   .. code-block:: bash

       git clone https://github.com/ppp-one/astra.git
       cd astra

2. Create a virtual environment with conda:

   .. code-block:: bash

       conda create -n astra python=3.11
       conda activate astra

3. Install Astra in development mode:

   .. code-block:: bash

       pip install -e .

This will install Astra and all its dependencies.

Running Astra
-----------

To run Astra:

1. Ensure your Alpaca-compatible equipment (or simulators) is active on your network
2. Run the following command:

   .. code-block:: bash

       python src/astra/main.py

3. Follow the terminal instructions
4. Open a web browser and navigate to http://localhost:8000/ to access the Astra interface