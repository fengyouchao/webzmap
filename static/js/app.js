function update_job_status(){
   $.get("api/jobs", function(result){
        $("#tableBody").empty();
        $.each(result,function(n,value) {
           var data = {job: value, index:n}
           var html = template('jobRow', data);
           $("#tableBody").append(html);
        });
    });
}

$(document).ready(function(){
    update_job_status();
});
