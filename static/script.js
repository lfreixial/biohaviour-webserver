		function isNumber(evt) {
		evt = (evt) ? evt : window.event;
		var charCode = (evt.which) ? evt.which : evt.keyCode;
		if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
		}
		
		return true;
		}
		
var close = document.getElementsByClassName("closebtn");
var i;

for (i = 0; i < close.length; i++) {
  close[i].onclick = function(){
    var div = this.parentElement;
    div.style.opacity = "0";
    setTimeout(function(){ div.style.display = "none"; }, 600);
  }
}

		
		if(document.getElementById('mutate_True').checked == true) {   
         document.write("Summer radio button is selected");   

} else {  
         document.write("Summer radio button is not selected");   
}  
		

		
//<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
         e.style.display = 'none';
       else
          e.style.display = 'block';
		  
    }
//-->

		function show(){
  document.getElementById('div1').style.display ='none';
}

function hide(){

  document.getElementById('div1').style.display = 'block';
  
}

function getName(){
	return name
}



function validateForm(){
	
	var y = document.getElementById("generation").value;
	
	if (y.charAt(0) == 0 && y.toString().length == 1){
		if(document.getElementById('mutate_True').checked) {
		if (y >= 1){
			show();
		}
		else{
			hide();
		}
		}
	}
	else if (y.charAt(0) == 0 && y.toString().length > 1) {
		document.getElementById("generation").value = "0";
	}
	else{
		show();
	}
	
}
