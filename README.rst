A studyforrest.org dataset extension
************************************

|license| |access|

Eye movement events for the Forrest Gump movie
==============================================

Two groups of participants (each n=15) watched this movie. One in a lab setup,
another one in a MRI scanner. The original data are described in Hanke et al.
(2016, http://www.nature.com/articles/sdata201692). This dataset contains
eye movements results of fixations, saccades, post-saccadic oscillations,
and pursuit events. Details of the detection procedure are available in:

     Asim H. Dar, Adina S. Wagner & Michael Hanke (2019). `REMoDNaV: Robust
     Eye Movement Detection for Natural Viewing
     <https://github.com/psychoinformatics-de/paper-remodnav/blob/master/main.tex>`__

For more information about the project visit: http://studyforrest.org


Dataset content
---------------

For each participant and recording run in the original dataset, two files are
provided in this dataset:

- ``sub-??_task-movie_run-?_events.tsv``
- ``sub-??_task-movie_run-?_events.png``

The TSV files are BIDS-compliant event (text) files that contain one detected
eye movement event per line. For each event the following properties are given
(in columns):

- ``onset``: start time of an even, relative to the start of the recording (in
  seconds)
- ``duration``: duration of an event (in seconds)
- ``label``: event type label, known labels are:
  - ``FIXA``: fixation
  - ``PURS``: pursuit
  - ``SACC`/`ISAC``: saccade
  - ``LPSO`/`ILPS``: low-velocity post-saccadic oscillation 
  - ``HPSO`/`IHPS``: high-velocity post-saccadic oscillation 
- ``start_x``, ``start_y``: the gaze coordinate at the start of an event (in pixels)
- ``end_x``, ``end_y``: the gaze coordinate at the end of an event (in pixels)
- ``amp``: movement amplitude of an event (in degrees)
- ``peak_vel``: peak velocity of an event (in degrees/second)
- ``med_vel``: median velocity of an event (in degrees/second)
- ``avg_vel``: mean peak velocity of an event (in degrees/second)

The PNG files contain a visualization of the detected events together with
with the gaze coordinate time series, for visual quality control. The
algorithm parameters are also rendered into the picture.


How to obtain the dataset
-------------------------

This repository is a `DataLad <https://www.datalad.org/>`__ dataset. It provides
fine-grained data access down to the level of individual files, and allows for
tracking future updates. In order to use this repository for data retrieval,
`DataLad <https://www.datalad.org>`_ is required.
It is a free and open source command line tool, available for all
major operating systems, and builds up on Git and `git-annex
<https://git-annex.branchable.com>`__ to allow sharing, synchronizing, and
version controlling collections of large files. You can find information on
how to install DataLad at `handbook.datalad.org/en/latest/intro/installation.html
<http://handbook.datalad.org/en/latest/intro/installation.html>`_.

Get the dataset
^^^^^^^^^^^^^^^

A DataLad dataset can be ``cloned`` by running::

   datalad clone https://github.com/psychoinformatics-de/studyforrest-data-eyemovementlabels.git

Once a dataset is cloned, it is a light-weight directory on your local machine.
At this point, it contains only small metadata and information on the
identity of the files in the dataset, but not actual *content* of the
(sometimes large) data files.

Retrieve dataset content
^^^^^^^^^^^^^^^^^^^^^^^^

After cloning a dataset, you can retrieve file contents by running::

   datalad get <path/to/directory/or/file>

This command will trigger a download of the files, directories, or
subdatasets you have specified.

DataLad datasets can contain other datasets, so called *subdatasets*. If you
clone the top-level dataset, subdatasets do not yet contain metadata and
information on the identity of files, but appear to be empty directories. In
order to retrieve file availability metadata in subdatasets, run::

   datalad get -n <path/to/subdataset>

Afterwards, you can browse the retrieved metadata to find out about
subdataset contents, and retrieve individual files with ``datalad get``. If you
use ``datalad get <path/to/subdataset>``, all contents of the subdataset will
be downloaded at once.

Stay up-to-date
^^^^^^^^^^^^^^^

DataLad datasets can be updated. The command ``datalad update`` will *fetch*
updates and store them on a different branch (by default
``remotes/origin/master``). Running::

   datalad update --merge

will *pull* available updates and integrate them in one go.

Find out what has been done
^^^^^^^^^^^^^^^^^^^^^^^^^^^

DataLad datasets contain their history in the ``git log``.
By running ``git log`` (or a tool that displays Git history) in the dataset or on
specific files, you can find out what has been done to the dataset or to individual files
by whom, and when.

More information
^^^^^^^^^^^^^^^^

More information on DataLad and how to use it can be found in the DataLad Handbook at
`handbook.datalad.org <http://handbook.datalad.org/en/latest/index.html>`_. The
chapter "DataLad datasets" can help you to familiarize yourself with the
concept of a dataset.


.. |license|
   image:: https://img.shields.io/badge/license-PPDL-blue.svg
    :target: http://opendatacommons.org/licenses/pddl/summary
    :alt: PDDL-licensed

.. |access|
   image:: https://img.shields.io/badge/data_access-unrestricted-green.svg
    :alt: No registration or authentication required
