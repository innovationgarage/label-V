define([
  "labeler/group",
], function (
  Group,
) {
  function RootGroup(labeler) {
    if (!labeler) return;
    Group.apply(this, arguments);
  }
  RootGroup.prototype = new Group();
  RootGroup.prototype.constructor = RootGroup;
  RootGroup.prototype.isRoot = true;
 
  return RootGroup;
});
