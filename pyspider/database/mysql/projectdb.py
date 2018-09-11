#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-07-17 21:06:43

import time
import mysql.connector

from pyspider.database.base.projectdb import ProjectDB as BaseProjectDB
from pyspider.database.basedb import BaseDB
from .mysqlbase import MySQLMixin
try:
    import flask_login as login
except ImportError:
    from flask.ext import login


class ProjectDB(MySQLMixin, BaseProjectDB, BaseDB):
    __tablename__ = 'projectdb'

    def __init__(self, host='localhost', port=3306, database='projectdb',
                 user='root', passwd=None):
        self.database_name = database
        self.conn = mysql.connector.connect(user=user, password=passwd,
                                            host=host, port=port, autocommit=True)
        if database not in [x[0] for x in self._execute('show databases')]:
            self._execute('CREATE DATABASE %s' % self.escape(database))
        self.conn.database = database

        self._execute('''CREATE TABLE IF NOT EXISTS %s (
            `name` varchar(64) PRIMARY KEY,
            `group` varchar(64),
            `status` varchar(16),
            `script` TEXT,
            `version` int(10),
            `comments` varchar(1024),
            `rate` float(11, 4),
            `burst` float(11, 4),
            `createuser` varchar(64),
            `updateuser` varchar(64),
            `createtime` double(16, 4),
            `updatetime` double(16, 4)
            ) ENGINE=InnoDB CHARSET=utf8''' % self.escape(self.__tablename__))
        self._execute('''CREATE TABLE IF NOT EXISTS %s (
            `project` varchar(64),
            `script` TEXT,
            `version` int(10),
            `createuser` varchar(64),
            `createtime` double(16, 4),
            PRIMARY KEY (`project`,`version`)
            ) ENGINE=InnoDB CHARSET=utf8''' % self.escape('history'))
        self._execute('''CREATE TABLE IF NOT EXISTS %s (
            `name` varchar(64) PRIMARY KEY,
            `password` varchar(64),
            `createtime` double(16, 4),
            `updatetime` double(16, 4)
            ) ENGINE=InnoDB CHARSET=utf8''' % self.escape('users'))

    def insert(self, name, obj={}):
        obj = dict(obj)
        obj['name'] = name
        if login.current_user:
            obj['createuser'] = login.current_user.id
        obj['createtime'] = time.time()
        obj['updatetime'] = time.time()
        return self._insert(**obj)

    def insert_history(self, project, version, obj={}):
        obj = dict(obj)
        obj['project'] = project
        obj['version'] = version
        obj['createtime'] = time.time()
        if login.current_user:
            obj['createuser'] = login.current_user.id
        return self._insert(tablename='history', **obj)

    def update(self, name, obj={}, **kwargs):
        obj = dict(obj)
        obj.update(kwargs)
        obj['updatetime'] = time.time()
        if login.current_user:
            obj['updateuser'] = login.current_user.id
        ret = self._update(where="`name` = %s" %
                           self.placeholder, where_values=(name, ), **obj)
        return ret.rowcount

    def get_all(self, fields=None):
        return self._select2dic(what=fields)

    def get(self, name, fields=None):
        where = "`name` = %s" % self.placeholder
        for each in self._select2dic(what=fields, where=where, where_values=(name, )):
            return each
        return None

    def get_user(self, name, password):
        fields = ['name', 'password', 'updatetime']
        where = "`name` = %s and `password` = %s" % (
            self.placeholder, self.placeholder)
        for each in self._select2dic(tablename='users', what=fields, where=where, where_values=(name, password)):
            return each
        return None

    def drop(self, name):
        where = "`name` = %s" % self.placeholder
        return self._delete(where=where, where_values=(name, ))

    def check_update(self, timestamp, fields=None):
        where = "`updatetime` >= %f" % timestamp
        return self._select2dic(what=fields, where=where)
