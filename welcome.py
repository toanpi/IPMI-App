# Copyright 2015 APM . All Rights Reserved.
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
import os
import binascii
from flask import Flask, jsonify, request, redirect, render_template, send_file, url_for, send_from_directory, flash
from subprocess import call, Popen, PIPE
import datetime
from werkzeug import secure_filename
from ipmiarea import board_info, product_info, chassis_info, generate_ipmi_eeprom, parse_ipmi_eeprom
from error import message_header, file_info, checksum, status, dump_Popen_status
from frufile import validate
import sys  

reload(sys)  
sys.setdefaultencoding('latin-1')
# from goto import goto, label
# reload(sys)  
# sys.setdefaultencoding('latin-1')
# import pexpect
file_fru_eeprom_name = "None"
VERSION = "1.3 BETA"
DEFAULT_CHASSIS_INFO_NOT_AVAILABLE = "NA","NA","NA","NA"
DEFAULT_PRODUCT_INFO_NOT_AVAILABLE = "NA","NA","NA","NA","NA","NA","NA"

app = Flask(__name__)
app.debug = True
app.secret_key = 'toan_pi'

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt','bin'])

app.config['MAX_CONTENT_LENGTH'] = 64*1024*1024
# app.config['TEMPLATES_AUTO_RELOAD'] = True

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



class eeprom_info:
	eeprom_name = ""
	eeprom_size = ""


def scp(source, user, password, serverip, path, STDOUT):
	print "scp %s to %s@%s:%s" % (source, user, serverip, path)
	# Popen(["scp", source, "%s@%s:%s" % (user,serverip, path)],stdout = STDOUT).wait()
	scp_server = Popen(["./tscp.sh", source, "%s@%s:%s" %
		   (user, serverip, path), password], stdout = STDOUT)
	scp_output, scp_err =scp_server.communicate()
	print "Output Scp: \n %s" %scp_output
	print "Error: %s" %scp_err
	return scp_server.returncode

# @app.route('/')
# def Welcome():
	# return app.send_static_file('index.html')

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


@app.route("/fru", methods=['POST', 'GET'])
def WelcomeToFru():
	# today = datetime.date.today()
	# print str(datetime.date.today())
	if 'serial_number' not in request.args:
		serial_number = "SQCA-A00000"
	elif request.args.get('serial_number') == '':
		serial_number = "SQCA-A00000"
	else:
		serial_number = request.args.get('serial_number')
		print "serial_number: " + serial_number

	chassis_info_area = chassis_info("chassis_info_include",\
									"23",\
									"EV-883408-X2-MXB-1",\
									"SQCA-A00000")
	board_info_area = board_info("board_info_include",\
								"1",\
								str(datetime.date.today()),\
								"AppliedMicro (R)",\
								"OSPREY",\
								serial_number,\
								"EV-883832-X3-MB1-1",\
								"0")
	product_info_area = product_info('product_info_include',\
									'AppliedMicro (R)',\
									'OSPREY',\
									'EV-883408-X2-MXB-1',\
									'V1.0',\
									'SQCA-A00000',\
									'SQCA-A00000')
	global VERSION
	file_name =  board_info_area.product_name.bytes.lower()+"-"+board_info_area.serial_number.bytes.lower() + "-fru-eeprom-" + board_info_area.date + ".bin"
	# return app.send_static_file('fru_25_3_17.html')
	return render_template("generate.html", board_area_ver = board_info_area.board_area_ver,
						   date = board_info_area.date,
						   mfg_name = board_info_area.mfg_name.bytes,
						   product_name = board_info_area.product_name.bytes,
						   serial_number = board_info_area.serial_number.bytes,
						   part_number = board_info_area.part_number.bytes,
						   fru_file_id = board_info_area.fru_file_id.bytes,
						   chassis_type = chassis_info_area.chassis_type,
						   chassis_part_number = chassis_info_area.chassis_part_num.bytes,
						   chassis_serial_number = chassis_info_area.chassis_serial_num.bytes,
						   product_mfg_name = product_info_area.mfg_name.bytes,
						   produc_product_name = product_info_area.product_name.bytes,
						   product_part_number = product_info_area.product_part_num.bytes,
						   product_product_ver = product_info_area.product_ver.bytes,
						   product_serial_number = product_info_area.product_serial_num.bytes,
						   product_asset_tag = product_info_area.asset_tag.bytes,
						   file_name = file_name,
						   version = VERSION,
						   today = str(datetime.datetime.now())
						   )


@app.route("/generate", methods=['POST', 'GET'])
def WelcomeToGenerate():
	backup_folder = "/home/validation_local/fru"
	backup_serverip = "10.38.12.37"
	backup_user = "validation_local"
	wri_fru_err = "NA"
	wri_fru_output = "NA"
	wri_fru_code = 1
	write_fru_status = "NA"
	pri_fru_output = "NA"
	pri_fru_err = "NA"
	pri_fru_code = 1
	ping_bmc_err = "NA"
	ping_bmc_output = "NA"
	ping_bmc_code = 1

	# store_folder = "./bin"
	global file_fru_eeprom_name

	eeprom = eeprom_info()
	eeprom.eeprom_name = request.form.get('eeprom_name')
	eeprom.eeprom_size = request.form.get('eeprom_size')

	dump_eeprom_info(eeprom)
	if 'chassis_info_include_switch' not in request.form:
		chassis_info_area = chassis_info("NA","NA","NA","NA")
	else:
		chassis_info_area = chassis_info(request.form['chassis_info_include_switch'],\
										request.form['chassis_type'],\
										request.form['chassis_part_number'],\
										request.form['chassis_serial_number'])
		chassis_info_area.dump_chassis_info()

	board_info_area = board_info("board_info_include",\
								request.form['board_area_ver'],\
								request.form['date'],\
								request.form['mfg_name'],\
								request.form['product_name'],\
								request.form['serial_number'],\
								request.form['part_number'],\
								request.form['fru_file_id'])

	board_info_area.dump_board_info()
	if 'product_info_include_switch' not in request.form:
		product_info_area = product_info( "NA","NA","NA","NA","NA","NA","NA")

	else:
		product_info_area = product_info(request.form['product_info_include_switch'],\
									request.form['product_mfg_name'],\
									request.form['produc_product_name'],\
									request.form['product_part_number'],\
									request.form['product_product_ver'],\
									request.form['product_serial_number'],\
									request.form['product_asset_tag'])

		product_info_area.dump_product_info()

	user = request.form['user']
	password = request.form['password']
	serverip = request.form['serverip']
	path = request.form['path']

	scp_switch = request.form['scp_switch']
	write_fru_switch = request.form['write_fru_switch']

	print "scp_switch is: " + scp_switch
	print "write_fru_switch is: " + write_fru_switch

	dump_server_info(user, password, serverip, path)
	# file name
	# file_name="fru-%s-eeprom.bin" %(board.product_name.lower())
	file_name = request.form['file_name']

	file_fru_eeprom_name = file_name

	print "File name: " + file_fru_eeprom_name
	# Generate fru eeprom

	res = generate_ipmi_eeprom(board_info_area, chassis_info_area, product_info_area, file_name)

	if res == file_info.ERROR_SUPPORT_LATIN_1:
		gen_status = "Failed"
		print "Generate:" + bcolors.FAIL+" Failed!"+bcolors.ENDC
		return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE + file_info.ERROR_SUPPORT_LATIN_1,
		 				version = VERSION
		 				)
	else:
		gen_status = "Done"
		print "Generate:" + bcolors.OKGREEN+" Done!"+bcolors.ENDC
	# cp file
	cp = Popen(["cp", file_name, backup_folder],stdout = PIPE, stderr = PIPE)
	cp_output, cp_err = cp.communicate()
		# Scp eeprom file
	if scp_switch == "scp_en":
		res = scp(file_name, user, password, serverip, path, PIPE)
		if res != 0:
			file_location_2 = "NA"
			scp_status = "Failed"
			print "Scp:" + bcolors.FAIL+" Failed!"+bcolors.ENDC
		else:
			file_location_2 = "%s@%s:%s/%s" % (user, serverip, path,"")
			scp_status = "Done"
			print "Scp:" + bcolors.OKGREEN+" Done!"+bcolors.ENDC

	else:
		file_location_2 = "NA"
		scp_status = "NA"
		print bcolors.WARNING+"Don't Scp"+bcolors.ENDC
	# Write to Bmc 
	if write_fru_switch == "write_fru_en":
		ping_bmc = Popen(["ping",request.form['bmc_serverip'],"-c","2"],stdout = PIPE, stderr = PIPE)
		ping_bmc_output, ping_bmc_err = ping_bmc.communicate()
		ping_bmc_code = ping_bmc.returncode
		dump_Popen_status('Ping BMC',ping_bmc_output,ping_bmc_err,ping_bmc.returncode )
		if ping_bmc.returncode == 0:
			wri_fru = Popen(["ipmitool","-H",request.form['bmc_serverip'],"-U","ADMIN","-P","ADMIN","fru","write","0",file_name],stdout = PIPE, stderr = PIPE)
			wri_fru_output,wri_fru_err = wri_fru.communicate()
			wri_fru_code = wri_fru.returncode
			dump_Popen_status('Write to Fru',wri_fru_output,wri_fru_err, wri_fru.returncode)
			if wri_fru.returncode == 0:
				write_fru_status = "Done"
			else:
				write_fru_status = "Failed"
			pri_fru = Popen(["ipmitool","-H",request.form['bmc_serverip'],"-U","ADMIN","-P","ADMIN","fru","print"],stdout = PIPE, stderr = PIPE)
			pri_fru_output,pri_fru_err = pri_fru.communicate()
			pri_fru_code = pri_fru.returncode
			dump_Popen_status('Print fru', pri_fru_output, pri_fru_err, pri_fru.returncode)
			print "Write fru Epprom:" + bcolors.OKGREEN+" Done!"+bcolors.ENDC
		else:
			print bcolors.FAIL + "BMC not alive" + bcolors.ENDC
	else:
		print bcolors.WARNING+"Don't write fru Epprom"+bcolors.ENDC


	# rm file
	# call(["mv",file_name,store_folder])

	file_location_1 = "%s@%s:%s/" % (backup_user,
									   backup_serverip, backup_folder)
	global VERSION
	return render_template("gen_result.html", board_area_ver = board_info_area.board_area_ver,
						   date = board_info_area.date,
						   mfg_name = board_info_area.mfg_name.bytes,
						   product_name = board_info_area.product_name.bytes,
						   serial_number = board_info_area.serial_number.bytes,
						   part_number = board_info_area.part_number.bytes,
						   fru_file_id = board_info_area.fru_file_id.bytes,
						   chassis_type = chassis_info_area.chassis_type,
						   chassis_part_number = chassis_info_area.chassis_part_num.bytes,
						   chassis_serial_number = chassis_info_area.chassis_serial_num.bytes,
						   product_mfg_name = product_info_area.mfg_name.bytes,
						   produc_product_name = product_info_area.product_name.bytes,
						   product_part_number = product_info_area.product_part_num.bytes,
						   product_product_ver = product_info_area.product_ver.bytes,
						   product_serial_number = product_info_area.product_serial_num.bytes,
						   product_asset_tag = product_info_area.asset_tag.bytes,
						   file_location_1 = file_location_1,
						   file_location_2 = file_location_2,
						   file_name = file_name,
						   gen_status = gen_status,
						   scp_status = scp_status,
						   write_fru_status = write_fru_status,
						   wri_fru_output = wri_fru_output,
						   wri_fru_err = wri_fru_err,
						   wri_fru_code = wri_fru_code,
						   pri_fru_output = pri_fru_output,
						   pri_fru_err = pri_fru_err,
						   pri_fru_code = pri_fru_code,
						   ping_bmc_output = ping_bmc_output, 
						   ping_bmc_err = ping_bmc_err,
						   ping_bmc_code = ping_bmc_code,
						   write_fru_switch = write_fru_switch,
						   chassis_info_include = chassis_info_area.is_included,
						   product_info_include = product_info_area.is_included,
						   version = VERSION,
						   today = str(datetime.datetime.now())
						   )


@app.route("/download", methods=['POST', 'GET'])
def WelcomeToDownload():
	print "Download :"+file_fru_eeprom_name
	return send_file(file_fru_eeprom_name, attachment_filename=file_fru_eeprom_name, as_attachment=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route("/upload", methods=['POST', 'GET'])
def WelcomeToUpload():
	print "Upload file"

	if 'file' not in request.files:
		print('No file part')
		return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE +  "No file part !",
		 				version = VERSION
		 				)

	file = request.files['file']
	print "File Name: %s" %file.filename
	if file.filename == '':
		flash('No selected file')
		return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE + "No selected file !",
		 				version = VERSION
		 				)
		# return message_header.DIAG_TEAM_MESSAGE + "No selected file !"
		# return redirect(url_for('WelcomeToUpload'))

	size_file = request.content_length
    # Check if the file is one of the allowed types/extensions
	res = validate(file, size_file,file_info.MAX_FILE_SIZE, app.config['ALLOWED_EXTENSIONS'])

	if res == file_info.OVER_SIZE:
		return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE + "File size( ~ %d bytes) is too large!. " %(size_file) +\
									 "Max is %d bytes" %(file_info.MAX_FILE_SIZE),
		 				version = VERSION
		 				)
		# return message_header.DIAG_TEAM_MESSAGE + "File size( ~ %d bytes) is too large! <br \>" %(size_file) +\
				# message_header.DIAG_TEAM_MESSAGE + "Max is %d bytes" %(file_info.MAX_FILE_SIZE)
	elif res == file_info.UNSUPPORTED_FILE_TYPE:
		return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE + "Unsupported file type !" ,
		 				version = VERSION
		 				)
		# return message_header.DIAG_TEAM_MESSAGE + "Unsupported file type !" 
	else:
	    # Move the file form the temporal folder to
	    # the upload folder we setup
		file_name = res
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
		print "Uploaded file name: %s" %file_name

		upload_file = open("%s%s" % (app.config['UPLOAD_FOLDER'], file_name),"rb")

		res, chassis_info_area, board_info_area, product_info_area = parse_ipmi_eeprom(upload_file)

		if res == status.FAILE:
			return render_template('warning.html',
		 				diag_message = message_header.DIAG_TEAM_MESSAGE + chassis_info_area,
		 				version = VERSION
		 				)
			# return message_header.DIAG_TEAM_MESSAGE + checksum.BAD_HEADER_CHECKSUM
		# elif chassis_info_area == checksum.BAD_CHASSIS_INFO_CHECKSUM:
		# 	return render_template('warning.html',
		#  				diag_message = message_header.DIAG_TEAM_MESSAGE + checksum.BAD_CHASSIS_INFO_CHECKSUM ,
		#  				version = VERSION
		#  				)
		# 	# return message_header.DIAG_TEAM_MESSAGE + checksum.BAD_CHASSIS_INFO_CHECKSUM
		# elif board_info_area == checksum.BAD_BOARD_INFO_CHECKSUM:
		# 	return render_template('warning.html',
		#  				diag_message = message_header.DIAG_TEAM_MESSAGE + checksum.BAD_BOARD_INFO_CHECKSUM ,
		#  				version = VERSION
		#  				)
		# 	# return message_header.DIAG_TEAM_MESSAGE + checksum.BAD_BOARD_INFO_CHECKSUM
		# elif product_info_area == checksum.BAD_PRODUCT_INFO_CHECKSUM:
		# 	return render_template('warning.html',
		#  				diag_message = message_header.DIAG_TEAM_MESSAGE + checksum.BAD_PRODUCT_INFO_CHECKSUM,
		#  				version = VERSION
		#  				)
			# return message_header.DIAG_TEAM_MESSAGE + checksum.BAD_PRODUCT_INFO_CHECKSUM
		else: 
			pass

		chassis_info_area.dump_chassis_info()
		board_info_area.dump_board_info()
		product_info_area.dump_product_info()

	    # Redirect the user to the uploaded_file route, which
	    # will basicaly show on the browser the uploaded file
	# return render_template('fru_25_3_17.html')
	global VERSION
	return render_template("generate.html", board_area_ver = board_info_area.board_area_ver,
						   date = board_info_area.date,
						   mfg_name = board_info_area.mfg_name.bytes,
						   product_name = board_info_area.product_name.bytes,
						   serial_number = board_info_area.serial_number.bytes,
						   part_number = board_info_area.part_number.bytes,
						   fru_file_id = board_info_area.fru_file_id.bytes,
						   chassis_type = chassis_info_area.chassis_type,
						   chassis_part_number = chassis_info_area.chassis_part_num.bytes,
						   chassis_serial_number = chassis_info_area.chassis_serial_num.bytes,
						   product_mfg_name = product_info_area.mfg_name.bytes,
						   produc_product_name = product_info_area.product_name.bytes,
						   product_part_number = product_info_area.product_part_num.bytes,
						   product_product_ver = product_info_area.product_ver.bytes,
						   product_serial_number = product_info_area.product_serial_num.bytes,
						   product_asset_tag = product_info_area.asset_tag.bytes,
						   file_name = file_name,
						   version = VERSION,
						   today = str(datetime.datetime.now())
						   )
	# return redirect(url_for('uploaded_file',filename = filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
# 
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
@app.route('/about',methods=['POST', 'GET'])
def WelcomeToAbout():
    return render_template('about.html',
    						version = VERSION
    						)
@app.route('/ipmi_spec',methods=['POST', 'GET'])
def WelcomeToIpmiSpec():
    return render_template('ipmi_spec.html',
    						version = VERSION
    						)
@app.route('/bmc',methods=['POST', 'GET'])
def WelcomeToBmc():
	global VERSION
	return render_template('bmc.html',
    						bmc_serverip = "10.38.15.172",
    						today = str(datetime.datetime.now()),
    						version = VERSION
    						)
@app.route('/ping_bmc',methods=['POST', 'GET'])
def WelcomeToPingBmc():
	bmc_serverip = request.form['bmc_serverip']
	ping_bmc = Popen(["ping",bmc_serverip,"-c","2"],stdout = PIPE,stderr = PIPE)
	ping_bmc_output, ping_bmc_err = ping_bmc.communicate()
	dump_Popen_status('Ping BMC', ping_bmc_output, ping_bmc_err, ping_bmc.returncode)
	global VERSION
	return render_template('bmc.html',
    						ping_bmc_output =  ping_bmc_output,
    						ping_bmc_err = ping_bmc_err,
    						ping_bmc_code = ping_bmc.returncode,
    						bmc_serverip = bmc_serverip,
    						today = str(datetime.datetime.now()),
    						version = VERSION
    						)

@app.route('/write_fru',methods=['POST', 'GET'])
def WelcomeToWriteBmc():
	bmc_serverip = request.form['bmc_serverip']
	wri_fru = Popen(["ipmitool","-H",bmc_serverip,"-U","ADMIN","-P","ADMIN","fru","write","0",file_name],stdout = PIPE, stderr = PIPE)
	wri_fru_output,wri_fru_err = wri_fru.communicate()
	print "Out put write \n %s \n end" %wri_fru_output
	print "Err write: %s \n end" %wri_fru_err
	if wri_fru_err == None:
		write_fru_status = "Done"
	else:
		write_fru_status = "Failed"
	global VERSION
	return render_template('bmc.html',
							wri_fru_output = wri_fru_output,
							wri_fru_err = wri_fru_err,
							bmc_serverip = bmc_serverip,
							today = str(datetime.datetime.now()),
    						version = VERSION
    						)
@app.route('/print_fru', methods=['POST', 'GET'])
def WelcomeToPrintBmc():
	pri_fru_output = 'NA'
	pri_fru_err = 'NA'
	pri_fru_code = 1
	bmc_serverip = request.form['bmc_serverip']
	ping_bmc = Popen(["ping",bmc_serverip,"-c","2"],stdout = PIPE, stderr = PIPE)
	ping_bmc_output, ping_bmc_err = ping_bmc.communicate()
	dump_Popen_status('Ping BMC',ping_bmc_output,ping_bmc_err,ping_bmc.returncode )
	if ping_bmc.returncode == 0:
		pri_fru = Popen(["ipmitool","-H",bmc_serverip,"-U","ADMIN","-P","ADMIN","fru","print"],stdout = PIPE, stderr = PIPE)
		pri_fru_output,pri_fru_err = pri_fru.communicate()
		pri_fru_code = pri_fru.returncode
		dump_Popen_status('Print fru', pri_fru_output, pri_fru_err, pri_fru.returncode)
		print "Write fru Epprom:" + bcolors.OKGREEN+" Done!"+bcolors.ENDC
	else:
		pass
	global VERSION
	return render_template('bmc.html',
							ping_bmc_output = ping_bmc_output,
							ping_bmc_err = ping_bmc_err,
							ping_bmc_code = ping_bmc.returncode,
							pri_fru_output = pri_fru_output,
							pri_fru_err = pri_fru_err,
							pri_fru_code = pri_fru_code, 
							bmc_serverip = bmc_serverip,
							today = str(datetime.datetime.now()),
    						version = VERSION
    						)
 
port = os.getenv('PORT', '8001')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port), debug=True)
