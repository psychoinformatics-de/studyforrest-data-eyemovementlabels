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

This is a DataLad dataset. It can be installed via::

  datalad install \
      https://github.com/psychoinformatics-de/studyforrest-data-eyemovementlabels.git

once installed, any file content can be obtained via::

  datalad get <somepath>  # e.g.:  datalad get .

Please refer to https://www.datalad.org for information on how to install
DataLad, and how to work with DataLad datasets.


.. |license|
   image:: https://img.shields.io/badge/license-PPDL-blue.svg
    :target: http://opendatacommons.org/licenses/pddl/summary
    :alt: PDDL-licensed

.. |access|
   image:: https://img.shields.io/badge/data_access-unrestricted-green.svg
    :alt: No registration or authentication required
