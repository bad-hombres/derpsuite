/* Application Javascript */

$(".button-collapse").sideNav();

$(".module").click(function() {
    var elm = $(this);
    var data = {
      "module": elm.data("module-name")
    };

    $.ajax(url_map["use"], {
      method: "POST",
      contentType: "application/json charset=utf8",
      data: JSON.stringify(data),
      success: function(r, status, xhr) {
        $("#content").html(r);
        $("#status-module").html(elm.data("module-name"));
        $(".module").parent().removeClass("teal lighten-5");
        elm.parent().addClass("teal lighten-5");
      },
      error: function(xhr, status, error) {
        alert("Could not change module: " + status + " : " + error);
      }
  });
});

$(".workspace").click(function() {
  var elm = $(this);
  data = {
    "workspace": elm.data("workspace-name"),
    "action": "select"
  };

  $.ajax(url_map["workspace"] , {
    method: "POST",
    contentType: "application/json charset=utf8",
    data: JSON.stringify(data),
    success: function(r, status, xhr) {
      location.reload();
    },
    error: function(xhr, status, error) {
      alert("Could not change workspace: " + status + " : " + error);
    }
  });

});

$("#add-workspace").click(function() {
  var elm = $('#new-workspace');
  data = {
    "workspace": elm.val(),
    "action": "add"
  };

  $.ajax(url_map["workspace"], {
    method: "POST",
    contentType: "application/json charset=utf8",
    data: JSON.stringify(data),
    success: function(r, status, xhr) {
      location.reload();
    },      
    error: function(xhr, status, error) {
      alert("Could add workspace: " + status + " : " + error);
    }
  });

});

$(".delete-workspace").click(function() {
  var elm = $(this);
  data = {
    "workspace": elm.data("workspace-name"),
    "action": "delete"
  };

  $.ajax(url_map["workspace"], {
    method: "POST",
    contentType: "application/json charset=utf8",
    data: JSON.stringify(data),
    beforeSend: function() {
      return confirm("You sure you want to delete this workspace?");
    },
    success: function(r, status, xhr) {
      location.reload();
    },
    error: function(xhr, status, error) {
      alert("Could not delete workspace: " + status + " : " + error);
    }
  });

});

$('.show-table').click(function () {
  var elm = $(this);
  var data = {
    "target": elm.data("table")
  }
  
  if (typeof slider !== 'undefined') {
    // the variable is defined
    var r = slider.noUiSlider.get();
    data["range"] = r[0] + "-" + r[1];
  }

  $.ajax(url_map["show"], {
    method: "POST",
    contentType: "application/json charset=utf8",
    data: JSON.stringify(data),
    success: function(r, status, xhr) {
      $('#content').html(r);
    },
    error: function(xhr, status, error) {
      alert("Could not fetch table");
    }
  });
});

$('.show-console').click(function () {
  var elm = $(this);
  
  $.ajax(url_map["console"], {
    method: "GET",
    success: function(r, status, xhr) {
      $('#content').html(r);
    },
    error: function(xhr, status, error) {
      alert("Could not fetch console");
    }
  });
});
