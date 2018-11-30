2. Edit the ``/etc/promstat/promstat.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://promstat:PROMSTAT_DBPASS@controller/promstat
