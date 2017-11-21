define([
  "labeler"
], function (
  Labeler
) {
  sessionId = randomString(20);
  videoId = null;
  currentFrame = null;
  modified = false;
  loading = false;
  labeler = null;

  function randomString(n) {
    var r="";
    while(n--)r+=String.fromCharCode((r=Math.random()*62|0,r+=r>9?(r<36?55:61):48));
    return r;
  }

  function setModified(m) {
    if (!loading) {
      modified = m;
      $(".labeler").toggleClass("modified", m);
    }
  };

  function setLoading(m) {
    loading = m;
    $(".wait-loading").toggleClass("done", !m);
  };

  function loadFrame() {
    setLoading(true);
    async.series([
      function (cb) {
        window.location.hash = JSON.stringify({video: videoId, session: sessionId, frame:currentFrame});
        imageLoaded = cb;
        $("#frame").attr({src: "/video/" + videoId + "/image/" + currentFrame.toString()});
      },
      function (cb) {
        labeler.deleteLabels();
        $.getJSON('/video/' + videoId + '/session/' + sessionId + '/bboxes/' + currentFrame.toString(), function (data) {
          var w = $("#frame").innerWidth();
          var h = $("#frame").innerHeight();
          data.bboxes.map(function (bbox) {
            labeler.addLabel({p1: {x:bbox[0], y:bbox[1]}, p2: {x: bbox[0] + bbox[2], y: bbox[1] + bbox[3]}});
          });
          setLoading(false);
          setModified(false);
          cb();
        });             
      }
    ]);
   }
  function saveFrame(cb) {
    if (modified) {
      var newBboxes = labeler.labels.map(function (a) {
        var c = {
          left: Math.min(a.p1.x, a.p2.x),
          right: Math.max(a.p1.x, a.p2.x),
          top: Math.min(a.p1.y, a.p2.y),
          bottom: Math.max(a.p1.y, a.p2.y)
        };
        return [c.left, c.top, c.right - c.left, c.bottom - c.top];
      });
      console.log("SAVING MODIFICATIONS");
      $.ajax({
        url: '/video/' + videoId + '/session/' + sessionId + '/bboxes/' + currentFrame.toString(),
        type: "POST",
        data: JSON.stringify(newBboxes),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function (data) {
          cb();
        }
      });
    } else {
      console.log("NO MODIFICATIONS TO SAVE");
      cb();
    }
  }
  $(document).ready(function() {
    labeler = new Labeler($("#frame"));
    labeler.updateHandlers.push(function(event) { setModified(true); });

    $("#frame").on("load", function () {
      imageLoaded();
    });

    $("#fileuploader").uploadFile({
      url:"/video",
      fileName:"file",
      returnType: "json",
      onSuccess:function(files,data,xhr,pd) {
        videoId = data.id;
        currentFrame = 0;
        loadFrame();
        console.log(data);
      }
    });
    $("#next").click(function () {
      saveFrame(function () {
        currentFrame+=10;
        loadFrame();
      });
    });
    $("#prev").click(function () {
      saveFrame(function () {
        currentFrame-=10;
        loadFrame();
      });
    });

    if (window.location.hash != "") {
      var args = JSON.parse(window.location.hash.substr(1));
      videoId = args.video;
      sessionId = args.session;
      currentFrame = args.frame;
      loadFrame();
    }
  });

});
