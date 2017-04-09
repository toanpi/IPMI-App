# Copyright 2017 APM . All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# utf-8 latin-1

# -*- coding: utf-8 -*-
# import sys
import sys  
reload(sys)  
sys.setdefaultencoding('latin-1')
# reload(sys)  
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class message_header(object):
    """docstring for message_header"""

    DIAG_TEAM_MESSAGE =  "[Diag Team]: "

    def __init__(self):
        super(message_header, self).__init__()
        # self.arg = arg
class status(object):
    """docstring for status"""
    OK = 0
    FAILE = 1
    def __init__(self):
        super(status, self).__init__()
        # self.arg = arg
        
class file_info(object):
    """docstring for file_info"""
    MAX_FILE_SIZE =  16*1024
    OVER_SIZE = "Over size"
    UNSUPPORTED_FILE_TYPE = "Unsupported file type"
    ERROR_SUPPORT_LATIN_1 = " Invalid data ! (charset is Latin-1)"

    def __init__(self):
        super(file_info, self).__init__()
        # self.arg = arg
class checksum(object):
    """docstring for checksum"""
    BAD_CHECKSUM = "Bad checksum"
    BAD_HEADER_CHECKSUM = "Bad header commom checksum"
    BAD_CHASSIS_INFO_CHECKSUM = "Bad chassis info checksum"
    BAD_BOARD_INFO_CHECKSUM = "Bad board checksum"
    BAD_PRODUCT_INFO_CHECKSUM = "Bad product info checksum"
    GOOD_CHECKSUM = "Good Checksum"
    def __init__(self):
        super(checksum, self).__init__()
        # self.arg = arg
    
class ipmi_field(object):
    """docstring for ipmi_field"""
    board_area_size_is_over = 1
    board_date_is_over = 2
    len_name_is_over = 3
    
    def __init__(self):
        super(ipmi_field, self).__init__()
        # self.arg = arg
        
def dump_Popen_status(title, stdout, stderr, returncode):
    print bcolors.WARNING+title+bcolors.ENDC
    print "Output  : %s \n end" %stdout
    print "Err  : %s \n end" %stderr
    if returncode == 0:
        print "Return code : %r --> " %returncode + bcolors.OKGREEN +"OK" +bcolors.ENDC 
    else:
        print "Return code : %r --> " %returncode + bcolors.FAIL +"FAILED" +bcolors.ENDC 

