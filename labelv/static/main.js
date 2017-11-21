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
  videoMetadata = null;
    
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

  function loadMetadata() {
    $.getJSON('/video/' + videoId + '/session/' + sessionId + '/metadata', function (data) {
      videoMetadata = data;          
      $(".timeslider *").remove();
      var w = $(".timeslider").width();
      var frames = parseInt(data.video["@nb_frames"]);

      data['keyframes'].sort();
      data['keyframes'].map(function (keyframe) {
        var frameNode = $("<div class='keyframe'></div>");
        frameNode.css({left: (w * keyframe / frames).toString() + "px"});
        $(".timeslider").append(frameNode);
      });
    });        
  };

  function displayFrame() {
    if (!$(".timeslider .currentFrame").length) {
      $(".timeslider").append("<div class='currentFrame'></div>");
    }
    var w = $(".timeslider").width();
    var frames = parseInt(videoMetadata.video["@nb_frames"]);
    $(".timeslider .currentFrame").css({left: (w * currentFrame / frames).toString() + "px"});
  }
    
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
            labeler.addLabel({bbox:bbox});
          });
          setLoading(false);
          setModified(false);
          displayFrame();
          cb();
        });             
      }
    ]);
   }
  function saveFrame(cb) {
    if (modified) {
      var newBboxes = labeler.labels.map(function (a) {
        return a.toJSON().bbox;
      });
      console.log("SAVING MODIFICATIONS");
      $.ajax({
        url: '/video/' + videoId + '/session/' + sessionId + '/bboxes/' + currentFrame.toString(),
        type: "POST",
        data: JSON.stringify(newBboxes),
        contentType:"application/json; charset=utf-8",
        dataType:"json",
        success: function (data) {
          loadMetadata();
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

    $(".timeslider").click(function (e) {
      var offset = $(".timeslider").offset();
      var w = $(".timeslider").width();
      var frames = parseInt(videoMetadata.video["@nb_frames"]);
      currentFrame = Math.round(frames * (e.pageX - offset.left) / w);
      loadFrame();
    });
      
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
        currentFrame+=1;
        loadFrame();
      });
    });
    $("#prev").click(function () {
      saveFrame(function () {
        currentFrame-=1;
        loadFrame();
      });
    });
    $("#fast_next").click(function () {
      saveFrame(function () {
        currentFrame+=10;
        loadFrame();
      });
    });
    $("#fast_prev").click(function () {
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
      loadMetadata();
      loadFrame();
    }
  });

});
