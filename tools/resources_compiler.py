#!/usr/bin/env python3
#
# Copyright 2012 Emilie Gillet.
#
# Author: Emilie Gillet (emilie.o.gillet@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# See http://creativecommons.org/licenses/MIT/ for more information.
#
# -----------------------------------------------------------------------------
#
# Generates .cc and .h files for string, lookup tables, etc.

"""Compiles python string tables/arrays into .cc and .h files."""

import os
import string
import sys


class ResourceEntry(object):

  def __init__(self, index, key, value, dupe_of, table, in_ram):
    self._index = index
    self._in_ram = in_ram
    self._key = key
    self._value = value
    self._dupe_of = self._key if dupe_of is None else dupe_of
    self._table = table

  @property
  def variable_name(self):
    return '%s_%s' % (self._table.prefix.lower(), self._dupe_of)

  @property
  def declaration(self):
    c_type = self._table.c_type
    name = self.variable_name
    storage = ' IN_RAM' if self._in_ram else ''
    return 'const %(c_type)s %(name)s[]%(storage)s' % locals()

  def Declare(self, f):
    if self._dupe_of == self._key:
      # Dupes are not declared.
      f.write('extern %s;\n' % self.declaration)

  def DeclareAlias(self, f):
    prefix = self._table.prefix
    key = self._key.upper()
    index = self._index
    if self._table.python_type == str:
      comment = '  // %s' % self._value
      size = None
    else:
      comment = ''
      size = len(self._value)
    f.write('#define %(prefix)s_%(key)s %(index)d%(comment)s\n' % locals())
    if not size is None:
      f.write('#define %(prefix)s_%(key)s_SIZE %(size)d\n' % locals())

  def Compile(self, f):
    # Do not create declaration for dupes.
    if self._dupe_of != self._key:
      return

    declaration = self.declaration
    if self._table.python_type == float:
      f.write('%(declaration)s = {\n' % locals())
      n_elements = len(self._value)
      for i in range(0, n_elements, 4):
        f.write('  ')
        f.write(', '.join(
            '% 16.9e' % self._value[j]
            for j in range(i, min(n_elements, i + 4))))
        f.write(',\n')
      f.write('};\n')
    elif self._table.python_type == str:
      value = self._value
      f.write('static %(declaration)s = "%(value)s";\n' % locals())
    else:
      f.write('%(declaration)s = {\n' % locals())
      n_elements = len(self._value)
      for i in range(0, n_elements, 4):
        f.write('  ')
        f.write(', '.join(
            '%6d' % self._value[j] if self._value[j] < 1 << 31 else
            '%6dUL' % self._value[j]
            for j in range(i, min(n_elements, i + 4))))
        f.write(',\n')
      f.write('};\n')


class ResourceTable(object):

  def __init__(self, resource_tuple):
    self.name = resource_tuple[1]
    self.prefix = resource_tuple[2]
    self.c_type = resource_tuple[3]
    self.python_type = resource_tuple[4]
    self.ram_based_table = resource_tuple[5]
    self.entries = []
    self._ComputeIdentifierRewriteTable()
    keys = set()
    values = {}
    for index, entry in enumerate(resource_tuple[0]):
      if self.python_type == str:
        # There is no name/value for string entries
        key, value = entry, entry.strip()
      else:
        key, value = entry

      # Add a prefix to avoid key duplicates.
      in_ram = 'IN_RAM' in key
      key = key.replace('IN_RAM', '')
      key = self
```
