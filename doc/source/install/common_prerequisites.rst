Prerequisites
-------------

Before you install and configure the promstat service,
you must create a database, service credentials, and API endpoints.

#. To create the database, complete these steps:

   * Use the database access client to connect to the database
     server as the ``root`` user:

     .. code-block:: console

        $ mysql -u root -p

   * Create the ``promstat`` database:

     .. code-block:: none

        CREATE DATABASE promstat;

   * Grant proper access to the ``promstat`` database:

     .. code-block:: none

        GRANT ALL PRIVILEGES ON promstat.* TO 'promstat'@'localhost' \
          IDENTIFIED BY 'PROMSTAT_DBPASS';
        GRANT ALL PRIVILEGES ON promstat.* TO 'promstat'@'%' \
          IDENTIFIED BY 'PROMSTAT_DBPASS';

     Replace ``PROMSTAT_DBPASS`` with a suitable password.

   * Exit the database access client.

     .. code-block:: none

        exit;

#. Source the ``admin`` credentials to gain access to
   admin-only CLI commands:

   .. code-block:: console

      $ . admin-openrc

#. To create the service credentials, complete these steps:

   * Create the ``promstat`` user:

     .. code-block:: console

        $ openstack user create --domain default --password-prompt promstat

   * Add the ``admin`` role to the ``promstat`` user:

     .. code-block:: console

        $ openstack role add --project service --user promstat admin

   * Create the promstat service entities:

     .. code-block:: console

        $ openstack service create --name promstat --description "promstat" promstat

#. Create the promstat service API endpoints:

   .. code-block:: console

      $ openstack endpoint create --region RegionOne \
        promstat public http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        promstat internal http://controller:XXXX/vY/%\(tenant_id\)s
      $ openstack endpoint create --region RegionOne \
        promstat admin http://controller:XXXX/vY/%\(tenant_id\)s
