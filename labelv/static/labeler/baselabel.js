define([], function () {
  function BaseLabel(labeler, parent, attrs) {
    if (!labeler) return;
    this.__id__ =   BaseLabel.counter++;
    this.labeler = labeler;
    this.parent = parent;
    this.eventHandlers = {};
    this.selected = false;

    if (!this.isRoot) {
      this.labelNode = $("<div class='label label-" + this.constructor.name + "'><input type='text'></input></div>");
      this.titleNode = this.labelNode.find("input")
      this.labelNode.css({
        "-webkit-user-select": "none",
        "-khtml-user-select": "none",
        "-moz-user-select": "none",
        "-o-user-select": "none",
        "user-select": "none"
      });
      this.labeler.labelsNode.append(this.labelNode);

      this._click = this.click.bind(this);
      this._titleChange = this.titleChange.bind(this);

      this.labelNode.click(this._click);
      this.titleNode.change(this._titleChange);
    }

    this.load(attrs);
  };
  BaseLabel.counter = 0;
  BaseLabel.prototype.destroy = function (e) {
    var self = this;
    if (!this.isRoot) {
      this.parent.detachChild(this);
      this.labelNode.remove();
    }
  };
  BaseLabel.prototype.load = function (attrs) {
    this.attrs = $.extend({
      title: '',
      bbox: [0, 0, 0, 0]
    }, attrs);
    if (!this.attrs.title) this.attrs.title = '';
    this.redraw();
  };
  BaseLabel.prototype.ungroup = function () {
    var parent = this.parent;
    if (!parent.parent) return;
    parent.parent.attachChild(this);
    if (parent.children.length == 0) {
      parent.destroy();
    }
  };
  BaseLabel.prototype.toJSON = function () {
    return this.attrs;
  };
  BaseLabel.prototype.send = function (event, args) {
    var handlers = this.eventHandlers[event];
    if (handlers) {
      handlers.map(function (f) { f(event, args); });
    }
    if (this.parent) {
      this.parent.send(event, args);
    }
  };
  BaseLabel.prototype.on = function (event, handler) {
    if (!this.eventHandlers[event]) this.eventHandlers[event] = [];
    this.eventHandlers[event].push(handler);
  };
  BaseLabel.prototype.un = function (event, handler) {
    if (!this.eventHandlers[event]) return;
    this.eventHandlers[event] = this.eventHandlers[event].filter(function (f) {
      return f != handler;
    });
  };
  BaseLabel.prototype.titleChange = function () {
    this.attrs.title = this.titleNode.val();
  };    
  BaseLabel.prototype.focus = function () {
    this.labelNode.find("input").focus();
  };    
  BaseLabel.prototype.redraw = function () {
    this.send('change', {label: this});
    if (!this.isRoot) {
      this.titleNode.val(this.attrs.title);
      this.labelNode.css({
        left: this.attrs.bbox[0].toString() + "px",
        width: this.attrs.bbox[2].toString() + "px",
        top: this.attrs.bbox[1].toString() + "px",
        height: this.attrs.bbox[3].toString() + "px"
      });
    }
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
  return BaseLabel;
});
