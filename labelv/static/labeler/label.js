define([
  "labeler/baselabel"
], function (
  BaseLabel
) {

  function Label(labeler) {
    if (!labeler) return;
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
  Label.prototype.constructor = Label;
  Label.prototype.destroy = function (e) {
    var self = this;
    BaseLabel.prototype.destroy.apply(this, arguments);
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
    if (this.attrs.bbox[2] == 0 || this.attrs.bbox[3] == 0) {
      this.destroy();
    }
  };

  return Label;
});
