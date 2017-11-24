define([
  "labeler/label",
  "labeler/rootgroup"
], function (
  Label,
  RootGroup
) {
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
    this.labels = new RootGroup(this);
    this.currentLabel = null;
    this.attrs = {
      type: "Group",
      args: this.labels.attrs
    }
  };
  Labeler.prototype.load = function (attrs) {
    this.labels.load(attrs);
    this.attrs.args = this.labels.attrs;
  };
  Labeler.prototype.filterSelected = function (child) { return child.selected; };
  Labeler.prototype.deleteSelected = function () {
    this.labels.forEach({
      recurse: true,
      filter: this.filterSelected,
      map: function (child) {
        child.destroy();
      }
    });
  };
  Labeler.prototype.groupSelected = function () {
    this.labels.forEach({
      recurse: true,
      filter: this.filterSelected,
      group: function (children, parent) {
        if (children.length) {             
          parent.groupChildren(children);
        }
      }
    });        
  };
  Labeler.prototype.ungroupSelected = function () {
    this.labels.forEach({
      recurse: true,
      filter: this.filterSelected,
      map: function (child) {
        child.ungroup();
      }
    });
  };
  Labeler.prototype.keyUp = function (e) {
    if (e.which == 46) {
      this.deleteSelected();
    } else if (e.which == 45) { // insert
      this.groupSelected();
    } else if (e.which == 27) { // esc
      this.ungroupSelected();
    }
  };
  Labeler.prototype.mouseDown = function (e) {
    this.offset = this.imageNode.offset();
    this.currentLabel = this.labels.addLabel({bbox: [e.pageX - this.offset.left,
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
