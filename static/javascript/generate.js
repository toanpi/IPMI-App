function yesnoSelectScp(){
if(document.getElementById('scp').value=="scp_en"){
document.getElementById('if_scp_en').style.display="";
}
else{
document.getElementById('if_scp_en').style.display="none";
}
}
function yesnoSelectWriteFru(){
// alert("1");
if(document.getElementById('write_fru').value=="write_fru_en"){
  // alert("h1");
document.getElementById('if_write_fru_en').style.display="";
}
else{
  // alert("h2");
document.getElementById('if_write_fru_en').style.display="none";

}
}

var date = new Date();
var day = date.getDate();
var month = date.getMonth() + 1;
var year = date.getFullYear();
if (month < 10) month = "0" + month;
if (day < 10) day = "0" + day;
var today = year + "-" + month + "-" + day;
// document.getElementById('theDate').value = today;
var day_name=today; 
var board_name=document.getElementById('TheName').value.toLowerCase();
var file_name=board_name+"-"+"fru"+"-eeprom-"+day_name+".bin";
// document.getElementById("TheFileName").value=file_name;
yesnoSelectChassisInfo();
yesnoSelectProductInfo();
yesnoSelectScp();
yesnoSelectWriteFru();

// if(document.getElementById('scp').value=="scp_en"){
// document.getElementById('if_scp_en').style.display="";
// }
// else{
// document.getElementById('if_scp_en').style.display="none";
// }

// if(document.getElementById('write_fru').value=="write_fru_en"){
// document.getElementById('if_write_fru_en').style.display="";
// }
// else{
// document.getElementById('if_write_fru_en').style.display="none";
// }

// if(document.getElementById('product_info').checked==true){
// document.getElementById('if_include_product_info').style.display="";
// }
// else{
// document.getElementById('if_include_product_info').style.display="none";
// }
// if(document.getElementById('chassis_info').checked==true){
// document.getElementById('if_include_chassis_info').style.display="";
// }
// else{
// document.getElementById('if_include_chassis_info').style.display="none";
// }

function check(){
var date_change=document.getElementById('date').value;
var board_name_change=document.getElementById('board_product_name').value.toLowerCase();
var serial_number_change = document.getElementById('serial_number').value.toLowerCase();

var file_name_change=board_name_change+"-"+serial_number_change+"-"+"fru"+"-eeprom-"+date_change+".bin";
// alert("hrh");
// file_name_change = ignoreSpaces(file_name_change);
// alert("hrh2");
document.getElementById("TheFileName").value = file_name_change.split(' ').join('');
// alert("done");
// Things to do when the textbox changes
}


function yesnoSelectProductInfo(){
if(document.getElementById('product_info').checked==true){
document.getElementById('if_include_product_info').style.display="";
document.getElementById('product_mfg_name').setAttribute('required','');
document.getElementById('produc_product_name').setAttribute('required','');
document.getElementById('product_part_number').setAttribute('required','');
document.getElementById('product_product_ver').setAttribute('required','');
document.getElementById('product_serial_number').setAttribute('required','');
document.getElementById('product_asset_tag').setAttribute('required','');
}
else{
document.getElementById('if_include_product_info').style.display="none";
document.getElementById('product_mfg_name').removeAttribute('required');
document.getElementById('produc_product_name').removeAttribute('required');
document.getElementById('product_part_number').removeAttribute('required');
document.getElementById('product_product_ver').removeAttribute('required');
document.getElementById('product_serial_number').removeAttribute('required');
document.getElementById('product_asset_tag').removeAttribute('required');

}
}
function yesnoSelectChassisInfo(){

if(document.getElementById('chassis_info').checked==true){

document.getElementById('if_include_chassis_info').style.display="";
document.getElementById('chassis_type').setAttribute("required","");
// alert(2);
document.getElementById('chassis_part_number').setAttribute("required","");
document.getElementById('chassis_serial_number').setAttribute("required","");

}
else{

document.getElementById('if_include_chassis_info').style.display="none";
document.getElementById('chassis_type').removeAttribute("required");
document.getElementById('chassis_part_number').removeAttribute("required");
document.getElementById('chassis_serial_number').removeAttribute("required");
// alert(1);

}
}
function hide_chassis_info(){
  // alert("hello1");
 if(document.getElementById('total_body_chassis_info').style.display=="block"){

document.getElementById('total_body_chassis_info').style.display="none";
}
else{

document.getElementById('total_body_chassis_info').style.display="block"; 
  
}
}
function hide_board_info(){
 if(document.getElementById('total_body_board_info').style.display=="block"){

document.getElementById('total_body_board_info').style.display="none";
}
else{

document.getElementById('total_body_board_info').style.display="block"; 
  
}
}
function hide_product_info(){
 if(document.getElementById('total_body_product_info').style.display=="block"){

document.getElementById('total_body_product_info').style.display="none";
}
else{

document.getElementById('total_body_product_info').style.display="block"; 
  
}
}
function hide_file_info(){
 if(document.getElementById('total_body_file_info').style.display=="block"){

document.getElementById('total_body_file_info').style.display="none";
}
else{

document.getElementById('total_body_file_info').style.display="block"; 
  
}
}
function hide_parse_file_info(){
 if(document.getElementById('total_body_parse_file').style.display=="block"){

document.getElementById('total_body_parse_file').style.display="none";
}
else{

document.getElementById('total_body_parse_file').style.display="block"; 
  
}
}
