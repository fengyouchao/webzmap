function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}


function updateJobStatus(){
   $.get("api/jobs", function(result){
        $("#tableBody").empty();
        $.each(result,function(n,value) {
           var data = {job: value, index:n}
           var html = template('jobRow', data);
           $("#tableBody").append(html);
        });
    });
}


function getJobOptions(){
    var aj = $.ajax( {
        url:'/api/jobs',
        type:'options',
        cache:false,
        dataType:'json',
        success:function(data) {
            $("#selectWhiteListFile").empty();
            $("#selectWhiteListFile").append(template('fileOption', {file:{value:null,display_name:''}}))
            $("#selectBlackListFile").empty();
            $("#selectBlackListFile").append(template('fileOption', {file:{value:null,display_name:''}}))
            console.log("options success")
            console.log(data)
            whiteList = data.actions.POST.white_list_file.choices
            $.each(whiteList,function(n,file) {
               var data = {file: file}
               var html = template('fileOption', data);
               $('#selectWhiteListFile').append(html);
            });
            blackList = data.actions.POST.black_list_file.choices
            $.each(blackList,function(n,file) {
               var data = {file: file}
               var html = template('fileOption', data);
               $('#selectBlackListFile').append(html);
            });
        },
        error : function(request) {
            var data = eval('(' + request.responseText + ')');
            alert(data.detail);
         }
    });
}


$('#newJobModal').on('show.bs.modal',
function(event) {
 getJobOptions();
});

$('#newJobModal').on('hide.bs.modal',
function(event) {
});


function createJob(){
    var csrftoken = getCookie('csrftoken');
    $("#createJobButton").addClass('disabled');
    $.ajax({
        cache: true,
        type: "POST",
        url:'/api/jobs/',
        headers:{'X-CSRFToken':csrftoken},
        data:$('#newJobForm').serialize(),
        async: true,
        success: function(data) {
            $("#createJobButton").removeClass('disabled');
            $('#newJobModal').modal('hide');
            updateJobStatus();
        },
        error: function(request) {
            $("#createJobButton").removeClass('disabled');
            console.log(request)
            var data = eval('(' + request.responseText + ')');
            for(var key in data){
                alert(key+':'+data[key])
            }
        }
    });
}

function deleteJob(url){
    var csrftoken = getCookie('csrftoken');
    var aj = $.ajax( {
        url:url,
        type:'DELETE',
        data:$('#deleteJobForm').serialize(),
        headers:{'X-CSRFToken':csrftoken},
        async: true,
        cache:false,
        dataType:'json',
        success:function(data) {
            console.log(data)
            $('#deleteJobModal').modal('hide');
            updateJobStatus();
        },
        error : function(request) {
            console.log(request)
            var data = eval('(' + request.responseText + ')');
            alert(data.detail);
         }
    });
}


function showDeleteJobModal(url){
     $('#deleteJobModal').modal('show');
     $('#deleteButton').attr('onclick',"deleteJob('"+url+"')");
}

function showLog(id){
    $('#logModal').modal('show');
    url = '/static/' + id + '/job.log';
    $('#logContainer').empty();
    var aj = $.ajax( {
        url:url,
        type:'GET',
        cache:false,
        dataType:'text',
        success:function(data) {
            console.log(data)
            $('#logContainer').append(data);
        },
        error : function(request) {
            console.log(request)
            $('#logContainer').append("Get log failed");
         }
    });
}

function autoUpdateStatus(time){
    updateJobStatus();
    setTimeout("autoUpdateStatus("+time+")", time )
}

$(document).ready(function(){
    autoUpdateStatus(1000);
});