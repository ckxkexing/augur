# Copyright 2016-2018 Brian Warner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier:  Apache-2.0

# Git repo maintenance
#
# This script is responsible for cloning new repos and keeping existing repos up
# to date. It can be run as often as you want (and will detect when it's
# already running, so as not to spawn parallel processes), but once or twice per
# day should be more than sufficient. Each time it runs, it updates the repo
# and checks for any parents of HEAD that aren't already accounted for in the
# repos. It also rebuilds analysis data, checks any changed affiliations and
# aliases, and caches data for display.
import sys
import platform
import imp
import time
import datetime
import html.parser
import subprocess
import os
import getopt
import xlsxwriter
import configparser
import psycopg2
import json
import logging
from urllib.parse import urlparse

from augur.tasks.github.util.github_task_session import *
from augur.application.logs import AugurLogger
from logging import Logger

logger = logging.getLogger(__name__)

def get_database_args_from_env():

    db_str = os.getenv("AUGUR_DB")
    db_json_file_location = os.getcwd() + "/db.config.json"
    db_json_exists = os.path.exists(db_json_file_location)

    if not db_str and not db_json_exists:

        logger.error("ERROR no way to get connection to the database. \n\t\t\t\t\t\t    There is no db.config.json and the AUGUR_DB environment variable is not set\n\t\t\t\t\t\t    Please run make install or set the AUGUR_DB environment then run make install")
        sys.exit()

    credentials = {}
    if db_str:
        parsedArgs = urlparse(db_str)

        credentials['db_user'] = parsedArgs.username#read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
        credentials['db_pass'] = parsedArgs.password#read_config('Database', 'password', 'AUGUR_DB_PASSWORD', 'augur')
        credentials['db_name'] = parsedArgs.path.replace('/','')#read_config('Database', 'name', 'AUGUR_DB_NAME', 'augur')
        credentials['db_host'] = parsedArgs.hostname#read_config('Database', 'host', 'AUGUR_DB_HOST', 'localhost')
        credentials['db_port'] = parsedArgs.port#read_config('Database', 'port', 'AUGUR_DB_PORT', 5432)
    else:
        with open("db.config.json", 'r') as f:
            db_config = json.load(f)

        credentials['db_user'] = db_config["user"]#read_config('Database', 'user', 'AUGUR_DB_USER', 'augur')
        credentials['db_pass'] = db_config["password"]#read_config('Database', 'password', 'AUGUR_DB_PASSWORD', 'augur')
        credentials['db_name'] = db_config["database_name"]#read_config('Database', 'name', 'AUGUR_DB_NAME', 'augur')
        credentials['db_host'] = db_config["host"]#read_config('Database', 'host', 'AUGUR_DB_HOST', 'localhost')
        credentials['db_port'] = db_config["port"]#read_config('Database', 'port', 'AUGUR_DB_PORT', 5432)
    #print(credentials)
    return credentials



class FacadeConfig:
    """Legacy facade config that holds facade's database functionality
        
        This is mainly for compatibility with older functions from legacy facade.

        Initializes database when it encounters a database exception

    Attributes:
        cfg (FacadeConfig): Class that supports the config and database functionality from legacy facade.
        repos_processed (int): Counter for how many repos have been analyzed
        cursor (psycopg2.extensions.cursor): database cursor for legacy facade.
        logger (Logger): logger object inherited from the session object
        db (psycopg2.extensions.connection): database connection object for legacy facade.
        tool_source (str): String marking the source of data as from facade.
        data_source (str): String indicating that facade gets data from git
        tool_version (str): Facade version
        worker_options (dict): Config options for facade.
        log_level (str): Keyword indicating level of logging for legacy facade.
    """
    def __init__(self, logger: Logger):
        self.repos_processed = 0
        self.cursor = None
        self.logger = logger

        self.db = None

        #worker_options = read_config("Workers", "facade_worker", None, None)

        with DatabaseSession(logger) as session:
            config = session.config
            worker_options = config.get_section("Facade")

        if 'repo_directory' in worker_options:
            self.repo_base_directory = worker_options['repo_directory']
        else:
            self.log_activity('Error',"Please specify a \'repo_directory\' parameter"
                " in your \'Workers\' -> \'facade_worker\' object in your config "
                "to the directory in which you want to clone repos. Exiting...")
            sys.exit(1)

        self.tool_source = '\'Facade \''
        self.tool_version = '\'1.2.4\''
        self.data_source = '\'Git Log\''

        self.worker_options = worker_options

        # Figure out how much we're going to log
        #logging.basicConfig(filename='worker_{}.log'.format(worker_options['port']), filemode='w', level=logging.INFO)
        self.log_level = None #self.get_setting('log_level')


    #### Database update functions ####

    def increment_db(self, version):

        # Helper function to increment the database number

        increment_db = ("INSERT INTO settings (setting,value) "
            "VALUES ('database_version',%s)")
        self.cursor.execute(increment_db, (version, ))
        db.commit()

        print("Database updated to version: %s" % version)

    def update_db(self, version):

        # This function should incrementally step any version of the database up to
        # the current schema. After executing the database operations, call
        # increment_db to bring it up to the version with which it is now compliant.

        print("Legacy Facade Block for DB UPDATE. No longer used. ")

        print("No further database updates.\n")

    def migrate_database_config(self):

    # Since we're changing the way we store database credentials, we need a way to
    # transparently migrate anybody who was using the old file. Someday after a long
    # while this can disappear.

        try:
            # If the old database config was found, write a new config
            imp.find_module('db')

            db_config = configparser.ConfigParser()

            from db import db_user,db_pass,db_name,db_host
            from db import db_user_people,db_pass_people,db_name_people,db_host_people

            db_config.add_section('main_database')
            db_config.set('main_database','user',db_user)
            db_config.set('main_database','pass',db_pass)
            db_config.set('main_database','name',db_name)
            db_config.set('main_database','host',db_host)

            db_config.add_section('people_database')
            db_config.set('people_database','user',db_user_people)
            db_config.set('people_database','pass',db_pass_people)
            db_config.set('people_database','name',db_name_people)
            db_config.set('people_database','host',db_host_people)

            with open('db.cfg','w') as db_file:
                db_config.write(db_file)

            print("Migrated old style config file to new.")
        except:
            # If nothing is found, the user probably hasn't run setup yet.
            sys.exit("Can't find database config. Have you run setup.py?")

        try:
            os.remove('db.py')
            os.remove('db.pyc')
            print("Removed unneeded config files")
        except:
            print("Attempted to remove unneeded config files")

        return db_user,db_pass,db_name,db_host,db_user_people,db_pass_people,db_name_people,db_host_people

    #### Global helper functions ####

    def database_connection(self, db_host,db_user,db_pass,db_name, db_port, people, multi_threaded_connection):

    # Return a database connection based upon which interpreter we're using. CPython
    # can use any database connection, although MySQLdb is preferred over pymysql
    # for performance reasons. However, PyPy can't use MySQLdb at this point,
    # instead requiring a pure python MySQL client. This function returns a database
    # connection that should provide maximum performance depending upon the
    # interpreter in use.

    ##TODO: Postgres connections as we make them ARE threadsafe. We *could* refactor this accordingly: https://www.psycopg.org/docs/connection.html #noturgent


        # if platform.python_implementation() == 'PyPy':
        db_schema = 'augur_data'
        db = psycopg2.connect(
            host = db_host,
            user = db_user,
            password = db_pass,
            database = db_name,
            # charset = 'utf8mb4',
            port = db_port,
            options=f'-c search_path={db_schema}',
            connect_timeout = 31536000,)

        cursor = db.cursor()#pymysql.cursors.DictCursor)


        self.cursor = cursor
        self.db = db

        # Figure out how much we're going to log
        #self.log_level = self.get_setting('log_level')
        #Not getting debug logging for some reason.
        self.log_level = 'Debug'
        return db, cursor

    def get_setting(self, setting):

    # Get a setting from the database

        query = ("""SELECT value FROM settings WHERE setting=%s ORDER BY
            last_modified DESC LIMIT 1""")
        self.cursor.execute(query, (setting, ))
        # print(type(self.cursor.fetchone()))
        return self.cursor.fetchone()[0]#["value"]

    def update_status(self, status):

    # Update the status displayed in the UI

        query = ("UPDATE settings SET value=%s WHERE setting='utility_status'")
        self.cursor.execute(query, (status, ))
        self.db.commit()

    def log_activity(self, level, status):

    # Log an activity based upon urgency and user's preference.  If the log level is
    # "Debug", then just print it and don't save it in the database.

        log_options = ('Error','Quiet','Info','Verbose','Debug')
        self.logger.info("* %s\n" % status)
        if self.log_level == 'Debug' and level == 'Debug':
            return

        #if log_options.index(level) <= log_options.index(self.log_level):
        query = ("INSERT INTO utility_log (level,status) VALUES (%s,%s)")
        try:
            self.cursor.execute(query, (level, status))
            self.db.commit()
        except Exception as e:
            self.logger.info('Error encountered: {}\n'.format(e))

            db_credentials = get_database_args_from_env()

            # Set up the database
            db_user = db_credentials["db_user"]
            db_pass = db_credentials["db_pass"]
            db_name = db_credentials["db_name"]
            db_host = db_credentials["db_host"]
            db_port = db_credentials["db_port"]
            db_user_people = db_user
            db_pass_people = db_pass
            db_name_people = db_name
            db_host_people = db_host
            db_port_people = db_port
            # Open a general-purpose connection
            db,cursor = self.database_connection(
                db_host,
                db_user,
                db_pass,
                db_name,
                db_port, False, False)
            self.cursor.execute(query, (level, status))
            self.db.commit()


    def inc_repos_processed(self):
        self.repos_processed += 1


