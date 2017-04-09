function hide_fru_info(){
   // alert("hello1");
if(document.getElementById('total_body_fru_info').style.display=="block"){
document.getElementById('total_body_fru_info').style.display="none";
}
else{
document.getElementById('total_body_fru_info').style.display="block"; 
}
}
function hide_bmc_info(){
   // alert("hello1");
if(document.getElementById('total_body_bmc_info').style.display=="block"){
document.getElementById('total_body_bmc_info').style.display="none";
}
else{
document.getElementById('total_body_bmc_info').style.display="block"; 
}
}


function increse_serial_number(){
alert(document.getElementById('serial_number').value);
document.getElementById('serial_number').value = document.getElementById('serial_number').value +"hehe";
}