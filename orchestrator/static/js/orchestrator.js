
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

function add_row() {

    $(".js-upload-request").click(function () {
      $("#fileupload").click();
    });
  
    $("#fileupload").fileupload({
      dataType: 'json',
      sequentialUploads: true,
  
      start: function (e) {
        $("#modal-progress").modal("show");
      },
  
      stop: function (e) {
        $("#modal-progress").modal("hide");
      },
  
      progressall: function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        var strProgress = progress + "%";
        $(".progress-bar").css({"width": strProgress});
        $(".progress-bar").text(strProgress);
      },
  
      done: function (e, data) {
        if (data.result.is_valid) {
          $("#gallery tbody").prepend(
            "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
          )
        }
      }
  
    });
  
  });

  