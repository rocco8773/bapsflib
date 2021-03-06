Getting Started
===============

The :mod:`bapsflib` package has four key sub-packages:

* :mod:`bapsflib._hdf`

    This package contains the generic HDF5 utilities for mapping and
    accessing any HDF5 file generated at the
    `Basic Plasma Science Facility (BaPSF) <http://plasma.physics.ucla.edu/>`_
    at UCLA.  Typically there is no reason to directly access classes in
    this package, since these classes are typically sub-classed to
    provided specific access to HDF5 files generate by each plasma
    device at BaPSF.  For example, any data collected on the Large
    Plasma Device (LaPD) will be handled by the :mod:`bapsflib.lapd`
    package.  For now, one can access data collected on the Small
    Plasma Device (SmPD) and Enormous Toroidal Plasma Device (ETPD) by
    utilizing :class:`bapsflib._hdf.File`.

* :mod:`bapsflib.lapd`

    This package contains functionality for accessing HDF5 files
    generated by the LaPD (:class:`bapsflib.lapd.File`), LaPD parameters
    (:mod:`bapsflib.lapd.constants`), and LaPD specific tools
    (:mod:`bapsflib.lapd.tools`).  Look to :ref:`using_bapsflib_lapd`
    for details about the package.

* :mod:`bapsflib.plasma`

    .. warning:: package currently in development

    This package plasma constants and functions.

* :mod:`bapsflib.utils`

    This package is for developers and contributors.  It contains
    utilities used for constructing the :mod:`bapsflib` package.

In the future, packages for the Small Plasma Device (SmPD)
:mod:`bapsflib.smpd` and the Enormous Toroidal Device (ETPD)
:mod:`bapsflib.etpd` will be added, as well as, some
fundamental analysis and plasma diagnostic packages.