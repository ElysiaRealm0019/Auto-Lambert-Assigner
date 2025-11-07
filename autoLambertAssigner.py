import maya.api.OpenMaya as om
import maya.cmds as cmds
import sys

# 插件信息
PLUGIN_NAME = "autoLambertAssigner"  # 插件文件名
PLUGIN_VERSION = "1.0.0"
PLUGIN_COMMAND = "autoAssignLambert" # 我们在Maya中执行的命令

def assign_materials_logic():
    """
    这是插件的核心功能。
    它获取所选内容，并为每个选中的几何体创建、重命名和分配新的Lambert材质。
    """
    
    # 1. 获取所有选中的物体（仅限变换节点）
    selection = cmds.ls(selection=True, type='transform')
    
    if not selection:
        om.MGlobal.displayWarning("没有选择任何物体。请先选择几何体。")
        return

    created_materials = [] # 用于最后选中新材质，方便用户查看

    # 2. 遍历所有选中的物体
    for obj in selection:
        
        # 检查这是否是一个有效的几何体（有形状节点）
        shapes = cmds.listRelatives(obj, shapes=True, path=True)
        if not shapes:
            om.MGlobal.displayWarning(f"跳过 '{obj}'，因为它没有形状节点 (可能不是几何体)。")
            continue

        # 3. 获取物体名称并清理
        # 使用 split('|')[-1] 来获取长名称中的最后一个（避免路径问题）
        base_name = obj.split('|')[-1]
        
        # 移除命名空间（如果存在）
        if ':' in base_name:
            base_name = base_name.split(':')[-1]
            
        # 4. 定义新材质和SG的名称
        material_name = f"{base_name}_mat"
        sg_name = f"{base_name}_SG"

        try:
            # 5. 创建新的 Lambert 材质
            # 使用 shadingNode 并指定名称。如果该名称已存在，Maya会自动添加数字后缀。
            material = cmds.shadingNode('lambert', asShader=True, name=material_name)
            
            # 6. 创建对应的 Shading Group (SG)
            # SG 是将材质连接到物体的“集合”
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)

            # 7. 将材质连接到 Shading Group
            # 将材质的 .outColor 属性连接到 SG 的 .surfaceShader 属性
            cmds.connectAttr(f"{material}.outColor", f"{sg}.surfaceShader")

            # 8. 将 Shading Group (即材质) 赋予物体
            # 我们使用 forceElement 来确保分配
            cmds.sets(obj, edit=True, forceElement=sg)
            
            created_materials.append(material)

        except Exception as e:
            om.MGlobal.displayError(f"为 '{obj}' 创建材质时出错: {e}")

    if created_materials:
        # 选中所有新创建的材质，以便用户在 Hypershade 或属性编辑器中看到它们
        cmds.select(created_materials)
        om.MGlobal.displayInfo(f"成功为 {len(created_materials)} 个物体创建并分配了新材质。")


# -----------------------------------------------------------------------------
# 插件命令 (MPxCommand)
# -----------------------------------------------------------------------------

class AutoAssignCmd(om.MPxCommand):
    
    def __init__(self):
        # 构造函数
        super(AutoAssignCmd, self).__init__()

    def doIt(self, args):
        # 当Maya执行我们的命令 (autoAssignLambert) 时，会调用这个方法
        try:
            # 执行我们的核心功能
            assign_materials_logic()
        except Exception as e:
            # 捕获任何意外错误并报告
            error_msg = f"执行 {PLUGIN_COMMAND} 时出错: {e}"
            sys.stderr.write(error_msg)
            om.MGlobal.displayError(error_msg)

    @staticmethod
    def creator():
        # Maya 调用这个方法来创建命令的实例
        return AutoAssignCmd()

def initializePlugin(plugin):
    """
    加载插件时调用。
    """
    plugin_fn = om.MFnPlugin(plugin, "Your Name", PLUGIN_VERSION, "Any")
    try:
        # 注册我们的命令，这样Maya才能识别 "autoAssignLambert"
        plugin_fn.registerCommand(PLUGIN_COMMAND, AutoAssignCmd.creator)
    except Exception as e:
        error_msg = f"注册命令 {PLUGIN_COMMAND} 失败: {e}"
        sys.stderr.write(error_msg)
        om.MGlobal.displayError(error_msg)

def uninitializePlugin(plugin):
    """
    卸载插件时调用。
    """
    plugin_fn = om.MFnPlugin(plugin)
    try:
        # 注销我们的命令
        plugin_fn.deregisterCommand(PLUGIN_COMMAND)
    except Exception as e:
        error_msg = f"注销命令 {PLUGIN_COMMAND} 失败: {e}"
        sys.stderr.write(error_msg)
        om.MGlobal.displayError(error_msg)