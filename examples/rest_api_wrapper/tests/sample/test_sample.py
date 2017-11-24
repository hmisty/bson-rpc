#!/usr/bin/env python
#encoding:utf-8

def inc(x):
  return x + 1

def test_int():
  assert inc(3) == 4
  assert inc(0) == 1
  assert inc(1.1) == 2.1
  # assert inc(3) == 5
