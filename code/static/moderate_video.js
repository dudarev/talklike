//
// As mentioned at http://en.wikipedia.org/wiki/XMLHttpRequest
//
if( !window.XMLHttpRequest ) XMLHttpRequest = function()
{
try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
throw new Error("Could not find an XMLHttpRequest alternative.")
};

//
// Makes an AJAX request to a local server function w/ optional arguments
//
// functionName: the name of the server's AJAX function to call
// opt_argv: an Array of arguments for the AJAX function
//
function Request(function_name, opt_argv) {

if (!opt_argv)
opt_argv = new Array();

// Find if the last arg is a callback function; save it
var callback = null;
var len = opt_argv.length;
if (len > 0 && typeof opt_argv[len-1] == 'function') {
callback = opt_argv[len-1];
opt_argv.length--;
}
var async = (callback != null);

// Build an Array of parameters, w/ function_name being the first parameter
var params = new Array(function_name);
for (var i = 0; i < opt_argv.length; i++) {
params.push(opt_argv[i]);
}
var body = JSON.stringify(params);

// Create an XMLHttpRequest 'POST' request w/ an optional callback handler 
var req = new XMLHttpRequest();
req.open('POST', '/rpc', async);

req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
req.setRequestHeader("Content-length", body.length);
req.setRequestHeader("Connection", "close");

if (async) {
req.onreadystatechange = function() {
  if(req.readyState == 4 && req.status == 200) {
    var response = null;
    try {
     response = JSON.parse(req.responseText);
    } catch (e) {
     response = req.responseText;
    }
    callback(response);
  }
}
}

// Make the actual request
req.send(body);
}

// Adds a stub function that will pass the arguments to the AJAX call 
function InstallFunction(obj, functionName) {
obj[functionName] = function() { Request(functionName, arguments); }
}

// Server object that will contain the callable methods
var server = {};

// Insert 'Add' as the name of a callable method
InstallFunction(server, 'FetchTitle');
InstallFunction(server, 'SubmitMove');
InstallFunction(server, 'UpdateMove');
InstallFunction(server, 'DeleteMove');

// Handy "macro"
function $(id){
return document.getElementById(id);
}

// Client function that calls a server rpc and provides a callback
function doFetchTitle() {
var d = $('fetch_title');
d.value = 'Fetching ...'; d.disabled = true;
var b = $('video_title');
b.disabled = true;
server.FetchTitle($('ytid').value, onFetchSuccess);
}

// Callback for after a successful doAdd
function onFetchSuccess(response) {
$('video_title_submit').value = response;
$('video_title').value = response;
$('video_title').disabled=false;
$('fetch_title').disabled=false;
$('fetch_title').value='Get title';
}

function doTakeTitle(){
$('video_title_submit').value = $('video_title').value;
$('dance_type_submit').value = $('dance_type').value;
}

// Client function that calls a server rpc and provides a callback
function doSubmitMove() {
var d = $('submit_move');
d.value = 'Sending ...'; d.disabled = true;
var b = $('move_name');
b.disabled = true;
server.SubmitMove($('ytid').value, $('move_name').value, $('move_time').value, onSubmitSuccess);
}

// Callback for after a successful doAdd
function onSubmitSuccess(response) {
$('request_result').innerHTML = response+'<br>'
$('move_name').value = ''
$('move_name').disabled=false
$('submit_move').disabled=false
$('submit_move').value='Add move'
}

function doUpdateMove(){
    $('move_time_new').disable=true;
    $('move_name_new').disable=true;
    server.UpdateMove($('ytid').value, 
                  $('move_time_old').value,
                  $('move_name_old').value,
                  $('move_time_new').value,
                  $('move_name_new').value,
                  onUpdateSuccess);
    $('update_move').value='Updating ...'
    $('update_move').disable=true;
    $('delete_move').disable=true;
}

function doDeleteMove(){
    $('move_time_new').disable=true;
    $('move_name_new').disable=true;
    server.DeleteMove($('ytid').value, 
                  $('move_time_old').value,
                  $('move_name_old').value,
                  onDeleteSuccess);
    $('delete_move').value='Deleting ...'
    $('update_move').disable=true;
    $('delete_move').disable=true;
}

function onUpdateSuccess(response) {
    $('update_result').innerHTML = response+'<br>';
    $('move_time_old').value = '';
    $('move_name_old').value = '';
    $('move_time_new').value = '';
    $('move_name_new').value = '';
    $('update_move').value='Update';
    $('update_move').disable=false;
    $('delete_move').disable=false;
}

function onDeleteSuccess(response) {
    $('update_result').innerHTML = response+'<br>';
    $('move_time_old').value = '';
    $('move_name_old').value = '';
    $('move_time_new').value = '';
    $('move_name_new').value = '';
    $('delete_move').value='Delete';
    $('update_move').disable=false;
    $('delete_move').disable=false;
}

function FillMoveInfo(which){
    if (document.all||document.getElementById){
        text = document.getElementById(which.id).innerHTML;
        if (text.match(/(.*?):/)) {
            time = RegExp.$1;
        }
        document.getElementById("move_time_new").value = time;
        document.getElementById("move_time_old").value = time;
        document.getElementById("move_name_new").value = text.replace(/[0-9.\s]+:\s/,'');
        document.getElementById("move_name_old").value = text.replace(/[0-9.\s]+:\s/,'');
    }
}
