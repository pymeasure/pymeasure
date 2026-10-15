###############
Procedure class
###############

.. automodule:: pymeasure.experiment.procedure
    :members:

Data columns and units
======================

.. autoattribute:: pymeasure.experiment.procedure.Procedure.DATA_COLUMNS

    Override this list in a Procedure subclass to define the names and order of the recorded data columns.
    Use the full column names, including any unit suffixes, as keys in dictionaries emitted with the :code:`'results'` topic.

    Append a Pint unit in parentheses to declare a column's physical unit, for example :code:`'Voltage (V)'`.
    Unit expressions must not contain spaces; compound units such as :code:`'Speed (m/s)'` or :code:`'Speed (meter/second)'` are supported.
    Use :code:`(1)` for dimensionless values.
    An undefined unit name raises :class:`ValueError` when the Procedure is constructed.

    When :class:`~pymeasure.experiment.results.Results` stores a row:

    * Plain numeric values, such as Python :class:`int` and :class:`float` values, are assumed to already use the declared unit.
    * A :code:`pint.Quantity` or a string representing a quantity is converted to the declared unit.
      For example, :code:`'500 mV'` is stored as :code:`0.5` in a :code:`'Voltage (V)'` column.
    * A quantity with incompatible dimensions, or a value that cannot be converted to the declared unit, is stored as :code:`nan` and a warning is logged.
      This also applies to booleans in columns with a declared unit.

    Columns without a unit suffix can store strings and booleans without unit conversion.
    If such a column receives a non-dimensionless :code:`pint.Quantity`, its base unit is adopted for that column's subsequent values.
    For example, a quantity of :code:`5 km` is stored as :code:`5000.0`, and later quantities in that column are converted to meters.
    Declare units in :attr:`DATA_COLUMNS` when they are known, rather than relying on this inference.
