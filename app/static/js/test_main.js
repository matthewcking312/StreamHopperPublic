(function ($) {
    "use strict";

	function validate1(val) {
	v1 = document.getElementById("fname");
	v2 = document.getElementById("lname");
	v3 = document.getElementById("email");
	v4 = document.getElementById("mob");

	flag1 = true;
	flag2 = true;
	flag3 = true;
	flag4 = true;

	if(val>=1 || val==0) {
		if(v1.value == "") {
		v1.style.borderColor = "red";
		flag1 = false;
		}
		else {
		v1.style.borderColor = "green";
		flag1 = true;
		}
	}

	if(val>=2 || val==0) {
		if(v2.value == "") {
		v2.style.borderColor = "red";
		flag2 = false;
		}
		else {
		v2.style.borderColor = "green";
		flag2 = true;
		}
	}

	if(val>=3 || val==0) {
		if(v3.value == "") {
		v3.style.borderColor = "red";
		flag3 = false;
		}
		else {
		v3.style.borderColor = "green";
		flag3 = true;
	}
	}

	if(val>=4 || val==0) {
		if(v4.value == "") {
		v4.style.borderColor = "red";
		flag4 = false;
		}
		else {
		v4.style.borderColor = "green";
		flag4 = true;
		}
	}

	flag = flag1 && flag2 && flag3 && flag4;

	return flag;
}

function validate2(val) {
	v1 = document.getElementById("cname");
	v2 = document.getElementById("zip");
	v3 = document.getElementById("state");
	v4 = document.getElementById("city");

	flag1 = true;
	flag2 = true;
	flag3 = true;
	flag4 = true;

	if(val>=1 || val==0) {
		if(v1.value == "") {
			v1.style.borderColor = "red";
			flag1 = false;
		}
		else {
		v1.style.borderColor = "green";
		flag1 = true;
		}
	}

	if(val>=2 || val==0) {
		if(v2.value == "") {
		v2.style.borderColor = "red";
		flag2 = false;
		}
		else {
		v2.style.borderColor = "green";
		flag2 = true;
		}
	}

if(val>=3 || val==0) {
if(v3.value == "") {
v3.style.borderColor = "red";
flag3 = false;
}
else {
v3.style.borderColor = "green";
flag3 = true;
}
}

if(val>=4 || val==0) {
if(v4.value == "") {
v4.style.borderColor = "red";
flag4 = false;
}
else {
v4.style.borderColor = "green";
flag4 = true;
}
}

flag = flag1 && flag2 && flag3 && flag4;

return flag;
}

$(document).ready(function(){

	var current_fs, next_fs, previous_fs;

$(".next").click(function(){

str1 = "next1";
str2 = "next2";
str3 = "next3";

if(!str2.localeCompare($(this).attr('id')) && validate1(0) == true) {
val2 = true;
}
else {
val2 = false;
}

if(!str3.localeCompare($(this).attr('id')) && validate2(0) == true) {
val3 = true;
}
else {
val3 = false;
}

if(!str1.localeCompare($(this).attr('id')) || (!str2.localeCompare($(this).attr('id')) && val2 == true) || (!str3.localeCompare($(this).attr('id')) && val3 == true)) {
current_fs = $(this).parent().parent();
next_fs = $(this).parent().parent().next();

$(current_fs).removeClass("show");
$(next_fs).addClass("show");

$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

current_fs.animate({}, {
step: function() {

current_fs.css({
'display': 'none',
'position': 'relative'
});

next_fs.css({
'display': 'block'
});
}
});
}
});

$(".prev").click(function(){

current_fs = $(this).parent().parent();
previous_fs = $(this).parent().parent().prev();

$(current_fs).removeClass("show");
$(previous_fs).addClass("show");

$("#progressbar li").eq($("fieldset").index(next_fs)).removeClass("active");

current_fs.animate({}, {
step: function() {

current_fs.css({
'display': 'none',
'position': 'relative'
});

previous_fs.css({
'display': 'block'
});
}
});
});

$('.radio-group .radio').click(function(){
$(this).toggleClass('selected');
});

})(jQuery);