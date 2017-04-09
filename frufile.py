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


from werkzeug import secure_filename
from error import  file_info, checksum
from ipmiarea import parse_ipmi_eeprom

reload(sys)  
sys.setdefaultencoding('latin-1')
# reload(sys)  
def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in allowed_extensions


def validate(file, size_file, limit_size, allowed_extensions):

    if size_file is not None and size_file > limit_size:
        return file_info.OVER_SIZE
        # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename, allowed_extensions):
        # Make the filename safe, remove unsupported chars
        file_name = secure_filename(file.filename)
        return file_name
    else:
        return file_info.UNSUPPORTED_FILE_TYPE

def check_ipmi_checksum(file_name, folder):

        upload_file = open("%s%s" % (folder, file_name),"rb")
        chassis_info_area, board_info_area, product_info_area = parse_ipmi_eeprom(upload_file)

        if chassis_info_area == checksum.BAD_HEADER_CHECKSUM:
            return checksum.BAD_HEADER_CHECKSUM
        elif chassis_info_area == checksum.BAD_CHASSIS_INFO_CHECKSUM:
            return checksum.BAD_CHASSIS_INFO_CHECKSUM
        elif board_info_area == checksum.BAD_BOARD_INFO_CHECKSUM:
            return checksum.BAD_BOARD_INFO_CHECKSUM
        elif product_info_area == checksum.BAD_PRODUCT_INFO_CHECKSUM:
            return checksum.BAD_PRODUCT_INFO_CHECKSUM
        else: 
            return checksum.GOOD_CHECKSUM
        
   