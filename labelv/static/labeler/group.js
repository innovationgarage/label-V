define([
  "labeler/baselabel",
  "labeler/label"
], function (
  BaseLabel,
  Label
) {
  function Group(labeler) {
    if (!labeler) return;
    this.children = [];
    BaseLabel.apply(this, arguments);
    
    this.on("add", this.handleChildUpdate.bind(this));
    this.on("change", this.handleChildUpdate.bind(this));
    this.on("delete", this.handleChildUpdate.bind(this));
  }
  Group.prototype = new BaseLabel();
  Group.prototype.constructor = Group;
  Group.prototype.destroy = function (e) {
    var self = this;
    BaseLabel.prototype.destroy.apply(this, arguments);
    this.children.map(function (child) {
      child.destroy();
    });
  };
  Group.prototype.handleChildUpdate = function (event, args) {
    if (args.label.parent === this) {
      var bboxes = this.attrs.children.map(function (child) { return child.args.bbox; });

      var l = Math.min.apply(null, bboxes.map(function (bbox) { return bbox[0]; }));
      var r = Math.max.apply(null, bboxes.map(function (bbox) { return bbox[0] + bbox[2]; }));
      var t = Math.min.apply(null, bboxes.map(function (bbox) { return bbox[1]; }));
      var b = Math.max.apply(null, bboxes.map(function (bbox) { return bbox[1] + bbox[3]; }));
            
      this.attrs.bbox = [l, t, r-l, b-t];
      this.redraw();
    }
  };
  Group.prototype.load = function (attrs) {
    var self = this;
    BaseLabel.prototype.load.apply(this, arguments);
    var children = this.attrs.children;
    this.children.map(function (child) { child.destroy(); });
    this.children = [];
    this.attrs.children = [];
    if (children) {
      children.map(function (child) {
        self['add' + child.type](child.args);
      });
    }
  };
  Group.prototype.detachChild = function (child) {
    this.send('delete', {label: child, parent: this});
    this.children = this.children.filter(function (label) {
      return label != child;
    });
    this.attrs.children = this.attrs.children.filter(function (label) {
      return label.args != child.attrs;
    });
  };
  Group.prototype.attachChild = function (child) {
    if (child.parent != this) {
      if (child.parent) {
        child.parent.detachChild(child);
      }
      child.parent = this;
    }
    this.children.push(child);
    this.attrs.children.push({type:child.constructor.name, args:child.attrs});
    // Update z-index
    if (child.forEach) {
      child.forEach({
        map: function (child) {
          if (!child.forEach) {
            child.redraw();
          }
        }
      })
    } else {
      child.redraw();
    }      
    this.send('add', {label: child, parent: this});
  };
  Group.prototype.addLabel = function (attrs) {
    var label = new Label(this.labeler, this, attrs);
    this.attachChild(label);
    return label;
  };
  Group.prototype.addGroup = function (attrs) {
    var group = new Group(this.labeler, this, attrs);
    this.attachChild(group);
    return group;
  };
  Group.prototype.forEach = function (args) {
    var self = this;
    args = $.extend({
      filter: undefined,
      map: undefined,
      group: undefined,
      recurse: true
    }, args);
    var children = this.children;

    if (args.recurse) {
      if (args.recurse !== true) {
        children = children.filter(function (child) {
          return args.recurse(child, self);
        });
      }
      children.map(function (child) {
        if (child.forEach) {
          child.forEach(args);
        }
      });
    }

    children = this.children;
    if (args.filter) {
      children = children.filter(function (child) {
        return args.filter(child, self);
      });
    }
    if (args.map) {
     children = children.map(function (child) {
       return args.map(child, self);
     });
    }
    if (args.group) {
      args.group(children, self);
    }
  };
  Group.prototype.groupChildren = function (children) {
    var newGroup = this.addGroup();

    children.map(function (child) {
      newGroup.attachChild(child);
    });
    return newGroup;
  };

  return Group;
});
