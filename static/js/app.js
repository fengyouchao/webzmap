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
    $("#createJobButton").addClass('disabled');
    $.ajax({
        cache: true,
        type: "POST",
        url:'/api/jobs/',
        data:$('#newJobForm').serialize(),
        async: true,
        success: function(data) {
            $("#createJobButton").removeClass('disabled');
            console.log(data)
            location.reload();
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
    var aj = $.ajax( {
        url:url,
        type:'DELETE',
        cache:false,
        dataType:'json',
        success:function(data) {
            console.log(data)
//            location.reload();
        },
        error : function(request) {
            console.log(request)
            var data = eval('(' + request.responseText + ')');
            alert(data.detail);
         }
    });
}

function getLog(id){
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

function showLog(id){
    $('#logModal').modal('show');
    getLog(id);
}


$(document).ready(function(){
    updateJobStatus();
    $("#createJobButton").click(function(){
        createJob();
    });
});