# Auto Lambert Assigner
Automaticly assigns Lambert materials for maya polygons and renames them according to the names of the polygons.

## 简介

很简单的小插件，用来给Maya里每一个多边形体附加默认的Lambert材质，并根据多边形体的名字重命名——这样子导入到SP的时候就不会乱套。

## 🚀 使用方法

在右下角的脚本编辑器中输入如下代码，也可以按住鼠标中键把它拖到工具架上：

```python
import maya.cmds as cmds
cmds.autoAssignLambert()
```

> **重要提示：** 请一定要选中所有你要操作的多边形体后再按执行。

-----

给个star吧 :P