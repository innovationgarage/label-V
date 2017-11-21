define([], function () {
  function Label(labeler, attrs) {
    this.labeler = labeler;
    this.labelNode = $("<div class='label'></div>");
    this.labelNode.css({
      "-webkit-user-select": "none",
      "-khtml-user-select": "none",
      "-moz-user-select": "none",
      "-o-user-select": "none",
      "user-select": "none"
    });
    this.selected = false;
    this.labeler.labelsNode.append(this.labelNode);

    $.extend(this, attrs);
    if (!this.p2) {
      this.p2 = $.extend({}, this.p1)
    }
      
    this.update(this.p2);
    this.updateSides = null;

    this._mouseDown = this.mouseDown.bind(this);
    this._mouseMove = this.mouseMove.bind(this);
    this._mouseUp = this.mouseUp.bind(this);
    this._click = this.click.bind(this);

    this.labelNode.mousedown(this._mouseDown);
    $("body").mousemove(this._mouseMove);
    $("body").mouseup(this._mouseUp);
    this.labelNode.click(this._click);
  };
  Label.prototype.update = function (p2) {
    this.p2 = p2;
    this.redraw();
  };
  Label.prototype.redraw = function () {
    this.labeler.updateHandlers.map(function (f) { f({label: self, event: 'change'}); });
    var coords = {
      left: Math.min(this.p1.x, this.p2.x),
      right: Math.max(this.p1.x, this.p2.x),
      top: Math.min(this.p1.y, this.p2.y),
      bottom: Math.max(this.p1.y, this.p2.y)
    };
    this.labelNode.css({
      left: coords.left.toString() + "px",
      width: (coords.right - coords.left).toString() + "px",
      top: coords.top.toString() + "px",
      height: (coords.bottom - coords.top).toString() + "px"
    });
  };
  Label.prototype.click = function (e) {
    this.selected = !this.selected;
    this.labelNode.toggleClass("selected", this.selected);
  };
  Label.prototype.mouseDown = function (e) {
    this.offset = this.labeler.imageNode.offset();
    var x = e.pageX - this.offset.left;
    var y = e.pageY - this.offset.top;
    this.updateSides = {x:"p1", y:"p1"};

    if (Math.abs(x - this.p1.x) > Math.abs(x - this.p2.x)) {
      this.updateSides.x = "p2";
    }
    if (Math.abs(y - this.p1.y) > Math.abs(y - this.p2.y)) {
      this.updateSides.y = "p2";
    }
  };
  Label.prototype.mouseMove = function (e) {
    if (this.updateSides != null) {
      this[this.updateSides.x].x = e.pageX - this.offset.left;
      this[this.updateSides.y].y = e.pageY - this.offset.top;
      this.redraw();
    }
  };
  Label.prototype.mouseUp = function (e) {
    this.updateSides = null;
  };
  Label.prototype.destroy = function (e) {
    var self = this;
    this.labeler.updateHandlers.map(function (f) { f({label: self, event: 'delete'}); });
    this.labelNode.unbind("mousedown", this._mouseDown);
    $("body").unbind("mousemove", this._mouseMove);
    $("body").unbind("mouseup", this._mouseUp);
    this.labelNode.remove();
    this.labeler.labels = this.labeler.labels.filter(function (label) { return label != self; });
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
    this._mouseMove = this.mouseMove.bind(this);
    this._mouseUp = this.mouseUp.bind(this);
    this._keyUp = this.keyUp.bind(this);

    this.imageNode.mousedown(this._mouseDown);
    $("body").mousemove(this._mouseMove);
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
    this.currentLabel = this.addLabel({p1: {x:e.pageX - this.offset.left,
                                            y:e.pageY - this.offset.top}});
  };
  Labeler.prototype.mouseMove = function (e) {
    if (this.currentLabel != null) {
      this.currentLabel.update({x:e.pageX - this.offset.left,
                                y:e.pageY - this.offset.top});
    }
  };
  Labeler.prototype.mouseUp = function (e) {
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
