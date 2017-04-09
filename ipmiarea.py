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
# from subprocess import call, Popen, PIPE
# from werkzeug import secure_filename
from datetime import datetime, timedelta
import error 
import sys  

reload(sys)  
sys.setdefaultencoding('latin-1')
# import pexpect
# reload(sys)  
# sys.setdefaultencoding('latin-1')

file_fru_eeprom_name = "None"

class commom_header(object):
	"""docstring for commom_header"""
	def __init__(self):
		super(commom_header, self).__init__()
		self.common_header_format_version = 1
		self.internal_use_area_starting_offset = 0
		self.chassis_info_area_starting_offset = 0
		self.board_area_starting_offset = 0
		self.product_info_area_starting_offset = 0
		self.multirecord_area_starting_offset = 0
		self.pad = 0
		self.common_header_checksum = 255
	def dump_commom_header(self):
		print bcolors.WARNING+"Commom header Info"+bcolors.ENDC
		print "	self.common_header_format_version %r" %self.common_header_format_version
		print "	self.internal_use_area_starting_offset %r" % self.internal_use_area_starting_offset
		print "	self.chassis_info_area_starting_offset %r" % self.chassis_info_area_starting_offset 
		print "	self.board_area_starting_offset %r" % self.board_area_starting_offset 
		print "	self.product_info_area_starting_offset %r" % self.product_info_area_starting_offset
		print "	self.multirecord_area_starting_offset %r" % self.multirecord_area_starting_offset
		print "	self.pad %r" % self.pad
		print "	self.common_header_checksum %r" % self.common_header_checksum
	def cal_check_sum(self):
		checksum = self.common_header_format_version +\
					self.internal_use_area_starting_offset +\
					self.chassis_info_area_starting_offset +\
					self.board_area_starting_offset +\
					self.product_info_area_starting_offset +\
					self.multirecord_area_starting_offset +\
					self.pad
		checksum = 256-(checksum % 256)
		return checksum

		
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def calc_checksum(s):
	sum = 0
	for c in s:
		sum += ord(c)
	sum = -(sum % 256)
	return (sum & 0xFF)
def str_zero_checksum(data):
	# print "Start check sum"
	checksum = 0
	for i in range(len(data)):
		checksum = checksum+ord(data[i])
	checksum = 256-(checksum % 256)
	return checksum

def int_zero_checksum(length, data):
	print "Start check sum"
	checksum = 0
	for i in range(length):
		checksum = checksum+data[i]
	checksum = 256-(checksum % 256)
	return checksum


def get_days(day_1, day_2, date_format):
	d0 = datetime.strptime(day_1, date_format)
	d1 = datetime.strptime(day_2, date_format)
	delta=abs(d0 - d1).days
	return delta

def time_mark(date,minute_num,date_format):
	d0 = datetime.strptime(date, date_format)
	date = d0 + timedelta(minutes=minute_num)
	return date

def get_ipmi_field_len(data):
	if data == "":
		return 0
	else:
		length = ord(data[0]) % (1<<6)
		# print "lenght data: %d" %length
		return length

def get_ipmi_field_type(data):
	if data == "":
		return 0
	else:
		type_code = ord(data[0]) / (1<<6)
		return type_code

def get_ipmi_field_bytes(type_code, data):
		type = get_ipmi_field_type(data)
		if type != type_code:
			print 'Unmap this type code: %r vs %r\n' %( type_code, type)
			return ""
		else:
			# print "get_ipmi_field_len: %d" % get_ipmi_field_len(data)
			return data[1:get_ipmi_field_len(data)+1]

def format_ipmi_field(type_code, data):
	# Format ipmi field as int array
	if len(data) >= (1<<6):
		return 0
	else:
		int_arr = []
		int_arr.append(type_code*(1 << 6) + len(data))
		for i in range(len(data)):
		# print chr(type_lenght)
			int_arr.append(ord(data[i]))			
		return  int_arr

class ipmi_info_field(object):
	"""docstring for ipmi_info_field"""
	offset = 0
	def __init__(self,type_code, data):
		super(ipmi_info_field, self).__init__()
		self.length = len(data) % (1<<6)
		self.type_code = type_code
		self.bytes = data
		self.header = type_code*(1<<6) + self.length 
		# self.data = format_ipmi_field(self.type_code, self.bytes) # int array 

def parse_ipmi_data(data):
		# print " data %r"  %data
		type_code = get_ipmi_field_type(data)
		bytes = get_ipmi_field_bytes(3,data)
		return ipmi_info_field(type_code, bytes)



def fill_info_area(offset, buffer, data, length, type_code):
	# Fill data(type string with lenght) to buffer at offset  
	if len(data) > (length):
		return error.ipmi_field.len_name_is_over
	else:
		print "type+len: %d+%d" % (type_code*(length), len(data))
		buffer[offset] = type_code*(length) + len(data)
		for i in range(0, len(data)):
			# print type(data[i])
			# print "data: "+data[i]
			if(type(data[i]) is unicode):
				buffer[offset+1+i] = ord(data[i])
			else:
				print "int"
				buffer[offset+1+i] = data[i]

		# print "mfg_name len: "+hex(data_eeprom[board_area_offset+7])
def string_2_int_arr(string):
	int_arr = []
	for i in range(len(string)):
		int_arr.append(ord(string[i]))
	print int_arr
	return int_arr

def copy_arr_2_arr (int_des,int_des_offset,int_scr,int_scr_offset, length):
	print "int_scr_offset: %d - int_des_offset: %d - lenght: %d" %(int_scr_offset,int_des_offset,length)
	print int_scr
	print int_des
	for i in range(length):
		int_des[i+int_des_offset] = int_scr[i+int_scr_offset]

class board_info(object):
	"""docstring for board_info"""
	def __init__(self, is_included, board_area_ver, date, mfg_name, product_name, serial_number, part_number, fru_file_id): 
		super(board_info, self).__init__()
		self.is_included = is_included
		self.start_addr = 0
		self.length = 0
		self.board_area_ver = board_area_ver
		self.date = date
		self.date_offset = 3
		self.mfg_name_offset = 6
		self.mfg_name = ipmi_info_field(3,mfg_name)
		self.product_name_offset = self.mfg_name_offset + self.mfg_name.length + 1
		self.product_name = ipmi_info_field(3,product_name)
		self.serial_number_offset = self.product_name_offset + self.product_name.length + 1
		self.serial_number = ipmi_info_field(3,serial_number)
		self.part_number_offset = self.serial_number_offset + self.serial_number.length + 1
		self.part_number = ipmi_info_field(3,part_number)
		self.fru_file_id_offset = self.part_number_offset + self.part_number.length + 1
		self.fru_file_id = ipmi_info_field(3,fru_file_id)
		# board_area_size
		self.board_area_size = 1+1+1+3+(1+self.mfg_name.length) + \
								(1+(self.product_name.length)) +\
								(1+(self.serial_number.length)) +\
								(1+(self.part_number.length)) +\
								(1+(self.fru_file_id.length)) +2
		# print board_area_size
		self.board_area_size = (self.board_area_size+8-(self.board_area_size % 8))

	def dump_board_info(self):
		print bcolors.WARNING+"Board Info"+bcolors.ENDC
		print "	Inclued: %s" % self.is_included
		print "	board_area_ver: %s" % self.board_area_ver
		print "	date: %s" % self.date
		print "	mfg_name: %s" % self.mfg_name.bytes
		print "	product_name: %s" % self.product_name.bytes
		print "	serial_number: %s" % self.serial_number.bytes
		print "	part_number: %s" % self.part_number.bytes
		print "	fru_file_id: %s" % self.fru_file_id.bytes

	def format_ipmi_board_info(self, board_area_data):
		print " format_ipmi_board_info "
		# Generate board information area data
		# board_area_data = []
		# board_area_size = 0
		type_code = 3  # 8 bit ASCII+1 Latin

		
		# board version
		for i in range(self.board_area_size):
			board_area_data.append(0)

		if int(self.board_area_ver, 0) > 255:
			return error.self_area_size_is_over
		else:
			board_area_data[0] = int(self.board_area_ver, 0)
		# print board_area_size
		board_area_data[1] = self.board_area_size/8

		# Wrire langue code : English
		# file.write(chr(int('0',0)))
		board_area_data[2] = 0 # or 25

		# Manafacturate date
		date_format = "%Y-%m-%d"
		days = get_days('1996-01-01',self.date,date_format)*24*60

		print "days: "+format(days, 'x')
		if len(format(days, 'x')) > 6:
			return error.ipmi_field.board_date_is_over
		else:
			for i in range(0, 3):
				board_area_data[3+i] = days % 256
				days = days/256
		# Mfg name
		# mfg_name_offset = 6
		fill_info_area(
			self.mfg_name_offset, board_area_data, self.mfg_name.bytes, 1 << 6, type_code)

		# Product_name
		# product_name_offset = mfg_name_offset+1+len(self.mfg_name)
		fill_info_area(
			self.product_name_offset, board_area_data, self.product_name.bytes, 1 << 6, type_code)

		# Serial_number
		# serial_number_offset = product_name_offset+1+len(self.product_name)
		fill_info_area(
			self.serial_number_offset, board_area_data, self.serial_number.bytes, 1 << 6, type_code)

		# part_number
		# part_number_offset = serial_number_offset+1+len(self.serial_number)
		fill_info_area(
			self.part_number_offset, board_area_data, self.part_number.bytes, 1 << 6, type_code)

		# fru_file_id
		# fru_file_id_offset = part_number_offset+1+len(self.part_number)
		fill_info_area(
			self.fru_file_id_offset, board_area_data, self.fru_file_id.bytes, 1 << 6, type_code)

		# C1h (type/length byte encoded to indicate no more info fields)
		board_area_data[1+self.fru_file_id_offset+self.fru_file_id.length] = 192  # C0
		board_area_data[1+self.fru_file_id_offset+self.fru_file_id.length + 1 ] = 193  # C1

		# Board Area Checksum (zero checksum)
		# print board_area_size
		board_area_data[
			self.board_area_size-1] = int_zero_checksum(self.board_area_size-1, board_area_data)
		# print board_area[board_area_size-1]
		print "Board area checksum : %r %s" % (board_area_data[self.board_area_size-1], hex(board_area_data[self.board_area_size-1]))
		# return board_area_data
		
	def get_info(self,board_area_data):
		print bcolors.WARNING + "Get board infomation" + bcolors.ENDC
		print "Data: \n" + board_area_data

		if str_zero_checksum(board_area_data[0:len(board_area_data)-1]) == ord(board_area_data[-1]):
			print bcolors.OKGREEN + "	Good checksum" + bcolors.ENDC
			pass
		else:
			print str_zero_checksum(board_area_data[0:len(board_area_data)-1])
			print ord(board_area_data[-1])
			print bcolors.FAIL + "	Bad checksum  " + bcolors.ENDC
			return error.checksum.BAD_BOARD_INFO_CHECKSUM

		self.board_area_ver = ord(board_area_data[0])
		self.length = ord(board_area_data[1]) * 8

		self.date_offset = 3
		self.date = ord(board_area_data[self.date_offset])+\
					ord(board_area_data[self.date_offset+1]) * (1<<8) +\
					ord(board_area_data[self.date_offset+2]) * (1<<16)
		date_format = "%Y-%m-%d"
		self.date = str(time_mark("1996-01-01",self.date,date_format))[0:10]
		print self.date

		self.mfg_name_offset = 6
		self.mfg_name = parse_ipmi_data(board_area_data[self.mfg_name_offset: len(board_area_data)])

		self.product_name_offset = self.mfg_name_offset + self.mfg_name.length + 1
		self.product_name = parse_ipmi_data(board_area_data[self.product_name_offset: len(board_area_data)])

		self.serial_number_offset = self.product_name_offset + self.product_name.length + 1
		self.serial_number = parse_ipmi_data(board_area_data[self.serial_number_offset: len(board_area_data)])

		self.part_number_offset = self.serial_number_offset + self.serial_number.length + 1
		self.part_number = parse_ipmi_data(board_area_data[self.part_number_offset: len(board_area_data)])

		self.fru_file_id_offset = self.part_number_offset + self.part_number.length + 1
		self.fru_file_id = parse_ipmi_data(board_area_data[self.fru_file_id_offset: len(board_area_data)])

		# print board_area_data[self.board_part_num_offset: len(board_area_data)]
		# self.dump_board_info()

class product_info(object):
	"""docstring for product_info"""
	def __init__(self, is_included, mfg_name, product_name, product_part_num, product_ver, product_serial_num, asset_tag): 
		super(product_info, self).__init__()
		self.is_included = is_included
		self.start_addr = 0
		self.length = 0
		if self.is_included == "product_info_include":
			self.product_area_ver = "1"
			self.mfg_name_offset = 3
			self.mfg_name = ipmi_info_field(3,mfg_name)
			self.product_name_offset = self.mfg_name_offset + self.mfg_name.length +1
			self.product_name = ipmi_info_field(3,product_name)
			self.product_part_num_offset = self.product_name_offset + self.product_name.length + 1
			self.product_part_num = ipmi_info_field(3,product_part_num)
			self.product_ver_offset = self.product_part_num_offset  + self.product_part_num.length + 1
			self.product_ver = ipmi_info_field(3,product_ver)
			self.product_serial_num_offset = self.product_ver_offset + self.product_ver.length + 1
			self.product_serial_num = ipmi_info_field(3,product_serial_num)
			self.asset_tag_offset = self.product_serial_num_offset + self.product_serial_num.length + 1
			self.asset_tag = ipmi_info_field(3,asset_tag)
			self.product_area_size = 1 + 1 + 1 + (1 + (self.mfg_name.length)) + \
									(1 + (self.product_name.length)) +\
									(1 + (self.product_part_num.length)) +\
									(1 + (self.product_ver.length)) +\
									(1 + (self.product_serial_num.length))+\
									(1 + (self.asset_tag.length)) +2
		else:
			self.product_area_ver = ipmi_info_field(3,"NA")

			self.mfg_name = ipmi_info_field(3,"NA")

			self.product_name = ipmi_info_field(3,"NA")

			self.product_part_num = ipmi_info_field(3,"NA")

			self.product_ver = ipmi_info_field(3,"NA")
			self.product_serial_num = ipmi_info_field(3,"NA")
			self.asset_tag = ipmi_info_field(3,"NA")
			self.product_area_size = 0

	def dump_product_info(self):
		print bcolors.WARNING + "Product info" + bcolors.ENDC
		print "	Inclued: %s" % self.is_included
		print "	Product area version: %s" % self.product_area_ver
		print "	Manufacturer Name: %s" % self.mfg_name.bytes
		print "	Product Name: %s" % self.product_name.bytes
		print "	Product Part Number: %s" % self.product_part_num.bytes
		print "	Product Version: %s" % self.product_ver.bytes
		print "	Product Serial Number: %s" % self.product_serial_num.bytes
		print "	Asset Tag: %s" % self.asset_tag.bytes

	def format_ipmi_product_info(self, product_area_data):
		print " format_ipmi_board_info "
		# Generate product information area data
		type_code = 3  # 8 bit ASCII+1 Latin
		# product_area_size
		# print product_area_size
		self.product_area_size = (self.product_area_size+8-(self.product_area_size % 8))
		# product version
		for i in range(self.product_area_size):
			product_area_data.append(0)

		if int(self.product_area_ver, 0) > 255:
			return error.self_area_size_is_over
		else:
			product_area_data[0] = int(self.product_area_ver, 0)
		# print self.product_area_size
		product_area_data[1] = self.product_area_size/8
		# Wrire langue code : English
		# file.write(chr(int('0',0)))
		product_area_data[2] = 0 # or 25
		# Mfg name
		
		fill_info_area(
			self.mfg_name_offset, product_area_data, self.mfg_name.bytes, 1 << 6, type_code)

		# Product_name
		fill_info_area(
			self.product_name_offset, product_area_data, self.product_name.bytes, 1 << 6, type_code)
		# product_part_num
		fill_info_area(
			self.product_part_num_offset, product_area_data, self.product_part_num.bytes, 1 << 6, type_code)
		# product_ver
		fill_info_area(
			self.product_ver_offset, product_area_data, self.product_ver.bytes, 1 << 6, type_code)
		# product_serial_num
		fill_info_area(
			self.product_serial_num_offset, product_area_data, self.product_serial_num.bytes, 1 << 6, type_code)
		# asset_tag
		fill_info_area(
			self.asset_tag_offset, product_area_data, self.asset_tag.bytes, 1 << 6, type_code)

		# C1h (type/length byte encoded to indicate no more info fields)
		product_area_data[1+self.asset_tag_offset+(self.asset_tag.length)] = 192  # C0
		product_area_data[1+self.asset_tag_offset+(self.asset_tag.length)+1] = 193  # C1
		# product Area Checksum (zero checksum)
		# print self.product_area_size
		product_area_data[
			self.product_area_size-1] = int_zero_checksum(self.product_area_size-1, product_area_data)
		# print product_area[self.product_area_size-1]
		print "product area checksum : %r %s" % (product_area_data[self.product_area_size-1], hex(product_area_data[self.product_area_size-1]))
		# return product_area_data
	def get_info(self,product_area_data):
		print bcolors.WARNING + "Get product infomation" + bcolors.ENDC
		print "Data: \n" + product_area_data
		if str_zero_checksum(product_area_data[0:len(product_area_data)-1]) == ord(product_area_data[-1]):
			print bcolors.OKGREEN + "	Good checksum" + bcolors.ENDC
			pass
		else:
			print str_zero_checksum(product_area_data[0:len(product_area_data)-1])
			print ord(product_area_data[-1])
			print bcolors.FAIL + "	Bad checksum  " + bcolors.ENDC
			return error.checksum.BAD_PRODUCT_INFO_CHECKSUM

		self.product_area_ver = ord(product_area_data[0])
		self.length = ord(product_area_data[1]) * 8

		self.mfg_name_offset = 3
		print "self.mfg_name_offset: %d" % self.mfg_name_offset
		# print product_area_data[self.product_part_num_offset: len(product_area_data)]
		self.mfg_name = parse_ipmi_data(product_area_data[self.mfg_name_offset: len(product_area_data)])

		self.product_name_offset = self.mfg_name_offset + self.mfg_name.length +1
		self.product_name = parse_ipmi_data(product_area_data[self.product_name_offset: len(product_area_data)])

		self.product_part_num_offset = self.product_name_offset + self.product_name.length + 1
		self.product_part_num = parse_ipmi_data(product_area_data[self.product_part_num_offset: len(product_area_data)])

		self.product_ver_offset = self.product_part_num_offset  + self.product_part_num.length + 1
		self.product_ver = parse_ipmi_data(product_area_data[self.product_ver_offset: len(product_area_data)])

		self.product_serial_num_offset = self.product_ver_offset + self.product_ver.length + 1
		self.product_serial_num = parse_ipmi_data(product_area_data[self.product_serial_num_offset: len(product_area_data)])

		self.asset_tag_offset = self.product_serial_num_offset + self.product_serial_num.length + 1
		self.asset_tag = parse_ipmi_data(product_area_data[self.asset_tag_offset: len(product_area_data)])

		# self.dump_product_info()	

class chassis_info(object):
	"""docstring for chassis_info"""
	length = 0
	type_code = 3
	def __init__(self, is_included, chassis_type, chassis_part_num, chassis_serial_num): 
		super(chassis_info, self).__init__()
		self.is_included = is_included
		if self.is_included == "chassis_info_include":
			self.chassis_area_ver = "1"
			self.chassis_type = chassis_type
			self.chassis_type_offset = 2
			self.chassis_part_num = ipmi_info_field(3,chassis_part_num)
			self.chassis_part_num_offset = 3
			self.chassis_serial_num = ipmi_info_field(3,chassis_serial_num)
			self.chassis_serial_num_offset = self.chassis_part_num_offset + self.chassis_part_num.length +1
			self.chassis_area_size = 1+1+1 + (1+self.chassis_part_num.length) +\
									(1+self.chassis_serial_num.length) + 2
		else:
			self.chassis_area_ver = "NA"
			self.chassis_type = "NA"
			self.chassis_type = "0"
			self.chassis_type_offset = 2
			self.chassis_part_num = ipmi_info_field(3,"NA")
			self.chassis_part_num_offset = 3
			self.chassis_serial_num = ipmi_info_field(3,"NA")
			self.chassis_serial_num_offset = self.chassis_part_num.length +1
		
	def dump_chassis_info(self):
		print bcolors.WARNING + "Chassis info" + bcolors.ENDC
		print "	Inclued: %s" % self.is_included
		print "	Chassis area ver: %s" % self.chassis_area_ver
		print "	Lenght : %r " % self.length
		print "	Chassis Type: %s" % self.chassis_type
		print "	Chassis Part Number: %s" % self.chassis_part_num.bytes
		print "	Chassis Serial Number: %s" % self.chassis_serial_num.bytes

	def format_ipmi_chassis_info(self,chassis_area_data):
		print " format_ipmi_chassis_info "
		# Generate chassis information area data
		# chassis_area_data = []
		# chassis_area_size = 0
		type_code = 3  # 8 bit ASCII+1 Latin

		# chassis_area_size
		
								
		self.chassis_area_size = (self.chassis_area_size + 8 - (self.chassis_area_size % 8))
		print "Chassis arae size : %d" %self.chassis_area_size
		# chassis version
		for i in range(self.chassis_area_size):
			chassis_area_data.append(0)

		if int(self.chassis_area_ver, 0) > 255:
			return error.self_area_size_is_over
		else:
			chassis_area_data[0] = int(self.chassis_area_ver, 0)
		# print self.chassis_area_size
		chassis_area_data[1] = self.chassis_area_size/8

		# chassis_type
		chassis_type_offset = 2
		chassis_area_data[chassis_type_offset] = int(self.chassis_type,0)
		print "Chassis type %r" %chassis_area_data[2] 
		# print chassis_part_num_offset
		fill_info_area(self.chassis_part_num_offset, chassis_area_data, self.chassis_part_num.bytes, 1 << 6, type_code)
		print "Chassis part number: bytes: %r - len: %d - offset %d " %(self.chassis_part_num.bytes,self.chassis_part_num.length,self.chassis_part_num_offset )
		chassis_area_data[self.chassis_part_num_offset]= self.chassis_part_num.header
		# copy_arr_2_arr(chassis_area_data,self.chassis_part_num_offset+1,string_2_int_arr(self.chassis_part_num.bytes),0,self.chassis_part_num.length )
		# # Serial_number
		fill_info_area(self.chassis_serial_num_offset, chassis_area_data, self.chassis_serial_num.bytes, 1 << 6, type_code)
		# copy_arr_2_arr(chassis_area_data,self.chassis_serial_num_offset+1,string_2_int_arr(self.chassis_serial_num.bytes),0,self.chassis_serial_num.length )
		# C1h (type/length byte encoded to indicate no more info fields)
		chassis_area_data[1+self.chassis_serial_num_offset+self.chassis_serial_num.length] = 192  # C1
		chassis_area_data[1+self.chassis_serial_num_offset+self.chassis_serial_num.length +1] = 193  # C1
		# Chassis Area Checksum (zero checksum)
		# print self.chassis_area_size
		chassis_area_data[
		 	self.chassis_area_size-1] = int_zero_checksum(self.chassis_area_size-1, chassis_area_data)
		print chassis_area_data
		# print chassis_area[self.chassis_area_size-1]
		print "chassis area checksum : %r %s" % (chassis_area_data[self.chassis_area_size-1], hex(chassis_area_data[self.chassis_area_size-1]))
		# return chassis_area_data
	
	def get_info(self,chassis_area_data):
		print bcolors.WARNING + "Get chassis infomation" + bcolors.ENDC
		print "Data: \n" + chassis_area_data

		if str_zero_checksum(chassis_area_data[0:len(chassis_area_data)-1]) == ord(chassis_area_data[-1]):
			print bcolors.OKGREEN + "	Good checksum" + bcolors.ENDC
			pass
		else:
			print str_zero_checksum(chassis_area_data[0:len(chassis_area_data)-1])
			print ord(chassis_area_data[-1])
			print bcolors.FAIL + "	Bad checksum  " + bcolors.ENDC
			return error.checksum.BAD_CHASSIS_INFO_CHECKSUM

		self.chassis_area_ver = ord(chassis_area_data[0])
		self.length = ord(chassis_area_data[1]) * 8

		self.chassis_type_offset = 2
		self.chassis_type = ord(chassis_area_data[2])

		self.chassis_part_num_offset = self.chassis_type_offset + 1
		print "self.chassis_part_num_offset: %d" % self.chassis_part_num_offset
		# print chassis_area_data[self.chassis_part_num_offset: len(chassis_area_data)]
		self.chassis_part_num = parse_ipmi_data(chassis_area_data[self.chassis_part_num_offset: len(chassis_area_data)])
		print "self.chassis_part_num.length : %d" %self.chassis_part_num.length
		self.chassis_serial_num_offset = self.chassis_part_num_offset + self.chassis_part_num.length + 1

		print self.chassis_serial_num_offset
		self.chassis_serial_num = parse_ipmi_data(chassis_area_data[self.chassis_serial_num_offset: len(chassis_area_data)])

		print self.chassis_type_offset
		if self.type_code != (self.chassis_part_num.type_code):
			print bcolors.WARNING+"Unsupport this type code"+ bcolors.ENDC
			return 1
		else:
			pass
			# self.dump_chassis_info()

class eeprom_info:
	eeprom_name = ""
	eeprom_size = ""



def dump_eeprom_info(eeprom):
	print bcolors.WARNING+"Eeprom Info"+bcolors.ENDC
	print "	eeprom_name: %s" % eeprom.eeprom_name
	print "	eeprom_size: %s" % eeprom.eeprom_size


def dump_server_info(user, password, serverip, path):
	print bcolors.WARNING+"File Location"+bcolors.ENDC
	print "	user: %s" % user
	print "	password: %s" % password
	print "	serverip: %s" % serverip
	print "	path: %s" % path


def generate_ipmi_eeprom(board, chassis, product, file_name):
	commom_header = []
	data_eeprom = []
	commom_header_size = 8
	data_eeprom_size = 448 # Max 512
	# test_checksum = [01, 03, 00, 00, 00, 00, 193, 65, 193, 79, 193, 65, 193, 49, 193, 52, 193]
	chassis_area_data = []
	board_area_data = []
	product_area_data = []

	print bcolors.WARNING+"Start generate fru eeprom"+bcolors.ENDC
	print "Make eeprom file"

	for i in range(commom_header_size):
		commom_header.append(0)
		# print commom_header[i]

	for i in range(data_eeprom_size):
		data_eeprom.append(255)
		# print board_area[i]
	file = open(file_name, "w")
	# file.write("Hello World!")
	# Generate commom header data
	commom_header[0] = 1
	commom_header[1] = 0
	commom_header[3] = 1   # Board Area Starting Offset : 0x08

	if chassis.is_included == "chassis_info_include":
		print bcolors.WARNING + "Include chassis info" + bcolors.ENDC
		commom_header[2] = 20  # Chassis Area Starting Offset : 0x50
	else:
		print bcolors.WARNING + "Not include chassis info" + bcolors.ENDC
		commom_header[2] = 0  # Chassis Area Starting Offset : NA


	if product.is_included == "product_info_include":
		print bcolors.WARNING + "Include product info" + bcolors.ENDC
		commom_header[4] = 30   # Product Area Starting Offset : 0x140
	else:
		print bcolors.WARNING + "Not include product info" + bcolors.ENDC
		commom_header[4] = 0  # Product Area Starting Offset : NA

	commom_header[5] = 0
	commom_header[6] = 0
	commom_header[7] = int_zero_checksum(7, commom_header)

	print "Checksum commom header: %s" % hex(commom_header[7])

	for i in range(0, commom_header_size):
		data_eeprom[i] = commom_header[i]

	board_area_offset = commom_header[3]*8
	chassis_area_offset = commom_header[2]*8
	product_area_offset = commom_header[4]*8
	# Generate board information area data

	# print "test checksum : %d hex:%s " % (int_zero_checksum(len(test_checksum), test_checksum), hex(int_zero_checksum(len(test_checksum), test_checksum)))

	board.format_ipmi_board_info(board_area_data)
	for i in range(0, len(board_area_data)):
		data_eeprom[i+board_area_offset] = board_area_data[i]

	
	if chassis.is_included == "chassis_info_include":
		chassis.format_ipmi_chassis_info(chassis_area_data)
		for i in range(0, len(chassis_area_data)):
			data_eeprom[i+chassis_area_offset] = chassis_area_data[i]
	else:
		print bcolors.WARNING + "Not include chassis info" + bcolors.ENDC

	
	if product.is_included == "product_info_include":
		product.format_ipmi_product_info(product_area_data)
		for i in range(0, len(product_area_data)):
			data_eeprom[i+product_area_offset] = product_area_data[i]
	else:
		print bcolors.WARNING + "Not include product info" + bcolors.ENDC

	for i in range(0, data_eeprom_size):
		if data_eeprom[i] > 255 :
			return error.file_info.ERROR_SUPPORT_LATIN_1
		else:
			file.write(chr(data_eeprom[i]))

	file.close()

	return 0

def get_ipmi_area(start_addr):
	print bcolors.WARNING + "Get chassis infomation" + bcolors.ENDC


def parse_ipmi_eeprom(file):
	commom_header_area = commom_header()
	# get commom header 
	file.seek(0)
	commom_header_area.common_header_format_version = ord(file.read(1))
	file.seek(1)
	commom_header_area.internal_use_area_starting_offset = ord(file.read(1))
	file.seek(2)
	commom_header_area.chassis_info_area_starting_offset = ord(file.read(1))
	file.seek(3)
	commom_header_area.board_area_starting_offset = ord(file.read(1))
	file.seek(4)
	commom_header_area.product_info_area_starting_offset = ord(file.read(1))
	file.seek(5)
	commom_header_area.multirecord_area_starting_offset = ord(file.read(1))
	file.seek(6)
	commom_header_area.pad = ord(file.read(1))
	file.seek(7)
	commom_header_area.common_header_checksum = ord(file.read(1))
	if commom_header_area.cal_check_sum() == commom_header_area.common_header_checksum:
		print bcolors.OKGREEN + "	Good checksum" + bcolors.ENDC
		pass
	else:
		print bcolors.FAIL + "	Bad checksum" + bcolors.ENDC
		return error.status.FAILE, error.checksum.BAD_HEADER_CHECKSUM, error.checksum.BAD_HEADER_CHECKSUM, error.checksum.BAD_HEADER_CHECKSUM

	commom_header_area.dump_commom_header()
	#parse chassis information
	chassis_info_area = chassis_info("Null","Null",'Null',"Null")
	file.seek(2)
	chassis_info_area.start_addr = ord(file.read(1)) * 8
	if chassis_info_area.start_addr ==0:
		pass
	else:
		print "Start address of chassis info: %r" %chassis_info_area.start_addr
		file.seek(chassis_info_area.start_addr + 1)
		chassis_info_area.length = (ord(file.read(1)) * 8)
		file.seek(chassis_info_area.start_addr)
		print "Chassis Area Lenght: %d" % chassis_info_area.length
		print "Chassis_info_len :%d" % chassis_info_area.length
		res = chassis_info_area.get_info( file.read(chassis_info_area.length))
		if res == error.checksum.BAD_CHASSIS_INFO_CHECKSUM :
			return error.status.FAILE, error.checksum.BAD_CHASSIS_INFO_CHECKSUM,  error.status.FAILE,  error.status.FAILE

	#parse product information
	product_info_area = product_info("Null","Null","Null","Null","Null","Null","Null")
	file.seek(4)
	product_info_area.start_addr = ord(file.read(1)) * 8
	if product_info_area.start_addr ==0:
		pass
	else:
		print "Start address of prduct info: %r" %product_info_area.start_addr
		file.seek(product_info_area.start_addr + 1)
		product_info_area.length = (ord(file.read(1)) * 8)
		file.seek(product_info_area.start_addr)
		print "Product Area Lenght: %d" % product_info_area.length
		print "Product_info_len :%d" % product_info_area.length
		res = product_info_area.get_info( file.read(product_info_area.length))
		if res == error.checksum.BAD_PRODUCT_INFO_CHECKSUM:
			return error.status.FAILE, error.checksum.BAD_PRODUCT_INFO_CHECKSUM, error.status.FAILE,  error.status.FAILE

	# parse board information 
	board_info_area = board_info("Null","Null","Null","Null","Null","Null","Null","Null")
	file.seek(3)
	board_info_area.start_addr = ord(file.read(1)) * 8
	if board_info_area.start_addr ==0:
		pass
	else:
		print "Start address of prduct info: %r" %board_info_area.start_addr
		file.seek(board_info_area.start_addr + 1)
		board_info_area.length = (ord(file.read(1)) * 8)
		file.seek(board_info_area.start_addr)
		print "Board Area Lenght: %d" % board_info_area.length
		print "Board_info_len :%d" % board_info_area.length
		res = board_info_area.get_info( file.read(board_info_area.length))
		if res == error.checksum.BAD_BOARD_INFO_CHECKSUM:
			return error.status.FAILE, error.checksum.BAD_BOARD_INFO_CHECKSUM,  error.status.FAILE,  error.status.FAILE

	return error.status.OK, chassis_info_area, board_info_area, product_info_area


