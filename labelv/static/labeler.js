define([], function () {
  function BaseLabel(labeler, attrs) {
    if (!labeler) return;
    this.labeler = labeler;
    this.labelNode = $("<div class='label'><input type='text'></input></div>");
    this.titleNode = this.labelNode.find("input")
    this.labelNode.css({
      "-webkit-user-select": "none",
      "-khtml-user-select": "none",
      "-moz-user-select": "none",
      "-o-user-select": "none",
      "user-select": "none"
    });
    this.labeler.labelsNode.append(this.labelNode);

    this.attrs = $.extend({}, attrs);
    if (!this.attrs.title) this.attrs.title = '';
    if (!this.attrs.selected) this.attrs.selected = false;
      
    this._click = this.click.bind(this);
    this._titleChange = this.titleChange.bind(this);
      
    this.labelNode.click(this._click);
    this.titleNode.change(this._titleChange);

    this.selected = false;
    this.redraw();
  };
  BaseLabel.prototype.destroy = function (e) {
    var self = this;
    this.labeler.updateHandlers.map(function (f) { f({label: self, event: 'delete'}); });
    this.labelNode.remove();
    this.labeler.labels = this.labeler.labels.filter(function (label) { return label != self; });
  };
  BaseLabel.prototype.toJSON = function () {
    return this.attrs;
  };
  BaseLabel.prototype.titleChange = function () {
    this.attrs.title = this.titleNode.val();
  };    
  BaseLabel.prototype.focus = function () {
    this.labelNode.find("input").focus();
  };    
  BaseLabel.prototype.redraw = function () {
    this.labeler.updateHandlers.map(function (f) { f({label: self, event: 'change'}); });
    this.titleNode.val(this.attrs.title);
    this.labelNode.css({
      left: this.attrs.bbox[0].toString() + "px",
      width: this.attrs.bbox[2].toString() + "px",
      top: this.attrs.bbox[1].toString() + "px",
      height: this.attrs.bbox[3].toString() + "px"
    });
  };
  BaseLabel.prototype.click = function (e) {
    this.selected = !this.selected;
    this.labelNode.toggleClass("selected", this.selected);
    this.focus();
  };
  BaseLabel.prototype.getBboxCoords = function () {
    return [
      this.attrs.bbox[0],
      this.attrs.bbox[1],
      this.attrs.bbox[0] + this.attrs.bbox[2],
      this.attrs.bbox[1] + this.attrs.bbox[3]
    ];
  };
  BaseLabel.prototype.setBboxCoords = function (coords) {
    l = Math.min(coords[0], coords[2]);
    r = Math.max(coords[0], coords[2]);
    t = Math.min(coords[1], coords[3]);
    b = Math.max(coords[1], coords[3]);
      
    this.attrs.bbox = [l, t, r-l, b-t];
  };

  function Label() {
    BaseLabel.apply(this, arguments);
    this.updateSides = null;

    this._mouseDown = this.mouseDown.bind(this);
    this._mouseMove = this.mouseMove.bind(this);
    this._mouseUp = this.mouseUp.bind(this);

    this.labelNode.mousedown(this._mouseDown);
    $("body").mousemove(this._mouseMove);
    $("body").mouseup(this._mouseUp);
  }
  Label.prototype = new BaseLabel();
  Label.prototype.destroy = function (e) {
    var self = this;
    BaseLabel.prototype.destroy.call(this, arguments);
    this.labelNode.unbind("mousedown", this._mouseDown);
    $("body").unbind("mousemove", this._mouseMove);
    $("body").unbind("mouseup", this._mouseUp);
  };
  Label.prototype.initiateMouseResize = function (x, y) {
    this.offset = this.labeler.imageNode.offset();
    this.updateSides = {x:x, y:y};
    this.coords = this.getBboxCoords();
  };
  Label.prototype.mouseDown = function (e) {
    this.offset = this.labeler.imageNode.offset();
    var mx = e.pageX - this.offset.left;
    var my = e.pageY - this.offset.top;
    var bbox = this.getBboxCoords();
    var x = 0;
    var y = 1;
      
    if (Math.abs(mx - bbox[0]) > Math.abs(mx - bbox[2])) {
      x = 2;
    }
    if (Math.abs(my - bbox[1]) > Math.abs(my - bbox[3])) {
      y = 3;
    }
    this.initiateMouseResize(x, y);
  };
  Label.prototype.mouseMove = function (e) {
    if (this.updateSides != null) {
      this.coords[this.updateSides.x] = e.pageX - this.offset.left;
      this.coords[this.updateSides.y] = e.pageY - this.offset.top;
      this.setBboxCoords(this.coords);
      this.redraw();
    }
  };
  Label.prototype.mouseUp = function (e) {
    this.updateSides = null;
  };
    
  function Labeler(img) {
    this.imageNode = $(img);
    this.imageNode.css({
      "-webkit-user-select": "none",
      "-khtml-user-select": "none",
      "-moz-user-select": "none",
      "-o-user-select": "none",
      "user-select": "none"
    });
    this.imageNode.wrap("<div class='labeler'></div>");
    this.labelerNode = this.imageNode.parent();
    this.labelsNode = $("<div class='labels' style=''></div>");
    this.labelerNode.prepend(this.labelsNode);

    this._mouseDown = this.mouseDown.bind(this);
    this._mouseUp = this.mouseUp.bind(this);
    this._keyUp = this.keyUp.bind(this);

    this.imageNode.mousedown(this._mouseDown);
    $("body").mouseup(this._mouseUp);
    $("body").keyup(this._keyUp);
    this.labels = [];
    this.currentLabel = null;
    this.updateHandlers = [];
  };
  Labeler.prototype.keyUp = function (e) {
    if (e.which == 46) {
      this.deleteLabels(function (label) { return label.selected; });
    }
  };
  Labeler.prototype.mouseDown = function (e) {
    this.offset = this.imageNode.offset();
    this.currentLabel = this.addLabel({bbox: [e.pageX - this.offset.left,
                                              e.pageY - this.offset.top,
                                              0, 0]});
    this.currentLabel.initiateMouseResize(2, 3);
  };
  Labeler.prototype.mouseUp = function (e) {
    if (this.currentLabel) {
      this.currentLabel.focus();
    }
    this.currentLabel = null;
  };
  Labeler.prototype.deleteLabels = function (test) {
    this.labels.map(function (label) {
      if (!test || test(label)) {
        label.destroy();
      }
    });
  };
  Labeler.prototype.addLabel = function (attrs) {
    var label = new Label(this, attrs);
    this.labels.push(label);
    this.updateHandlers.map(function (f) { f({label: label, event: 'add'}); });
    return label;
  };
  Labeler.prototype.destroy = function (e) {
    this.imageNode.unbind("mousedown", this._mouseDown);
    $("body").unbind("mousemove", this._mouseMove);
    $("body").unbind("mouseup", this._mouseUp);
    $("body").unbind("keyup", this._keyUp);
    this.labelsNode.remove();
    this.imageNode.unwrap();
  };
    
  return Labeler;
});
