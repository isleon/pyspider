#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2014-02-09 12:05:52

import time

from .sqlitebase import SQLiteMixin
from pyspider.database.base.projectdb import ProjectDB as BaseProjectDB
from pyspider.database.basedb import BaseDB
try:
    import flask_login as login
except ImportError:
    from flask.ext import login


class ProjectDB(SQLiteMixin, BaseProjectDB, BaseDB):
    __tablename__ = 'projectdb'
    placeholder = '?'

    def __init__(self, path):
        self.path = path
        self.last_pid = 0
        self.conn = None
        self._execute('''CREATE TABLE IF NOT EXISTS `%s` (
                name PRIMARY KEY,
                `group`,
                status, script, version, comments,
                rate, burst, 
                createuser, updateuser,
                createtime, updatetime
                )''' % self.__tablename__)
        self._execute('''CREATE TABLE IF NOT EXISTS `%s` (
                project, script, version,
                createtime, createuser
                )''' % 'history')
        self._execute('''CREATE TABLE IF NOT EXISTS `%s` (
                name PRIMARY KEY, password, 
                createtime, updatetime
                )''' % 'users')

    def insert(self, name, obj={}):
        obj = dict(obj)
        obj['name'] = name
        if login.current_user:
            obj['createuser'] = login.current_user.id
        obj['createtime'] = time.time()
        # obj['updatetime'] = time.time()
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

    def check_update(self, timestamp, fields=None):
        where = "`updatetime` >= %f" % timestamp
        return self._select2dic(what=fields, where=where)

    def drop(self, name):
        where = "`name` = %s" % self.placeholder
        return self._delete(where=where, where_values=(name, ))
