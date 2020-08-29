function searchClick() {
    var word = $("#word").val();
    if(word !=''){
    location.href = "/search/"+word;
    }
}

$("body").keydown(function() {
             if (event.keyCode == "13") {//keyCode=13是回车键
                 searchClick();
             }
         });