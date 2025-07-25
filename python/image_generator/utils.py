

def getShiftedUserDataID(user_data, num_layers, buildings_per_layer, layer_index, building_index, method='contain'):
    """
    将每层的偏移考虑进去后, 根据building_index获取当前位置的user_data_id
    """
    layer_data = user_data[layer_index]
    points_per_line = len(layer_data)
    idx = 0

    """
    contain方法:
    1. 横向划分为13个segment
    2. 假设共有两个图层, 
    第一层建筑的中点, 依次在0.25, 1.25, 2.25...12.25个segment的位置,
    第二层建筑的中点, 依次在0.75, 1.75, 2.75...12.75个segment的位置.
    
    这样能保证第一层和第二层交错显示, 完全等分全部图片的宽度. 

    在这种情况下, 返回的id不会越界
    """
    if method == 'contain':
        unit_offset = 1 / num_layers
        layer_offset = (layer_index+0.5) * unit_offset
        idx = int((building_index+layer_offset) / buildings_per_layer * (points_per_line - 1))

    """
    cover方法:
    1. 横向划分为(13-1)共12个segment. 若没有offset, 第一栋建筑中点横坐标为0, 最后一栋建筑中点横坐标为layer.width
    2. 假设共有两个图层, 
    第一层建筑的中点, 依次在-0.25, 0.75, 1.75...11.75个segment的位置,
    第二层建筑的中点, 依次在0.25, 1.25, 2.25...12.25个segment的位置.

    这样第一层和第二层交错显示. 但由于一共只有0 - 12个segment, 实际上, 会有建筑的中点在画框外的情况

    因此在这种情况下, 返回的id存在越界的情况.

    制作cover方法的原因是由于采用contain方式时:
    第一层实际上向左偏移, 这样会导致第一层最右端的建筑与图片右边缘较远, 留下一段缺少建筑物的折线, 显得匹配关系草草收尾. 
    
    但使用cover方法时同样存在问题:
    由于建筑物的中点一定存在出现在画框外的情况, 因此建筑物被裁切的情况更加严重. 甚至如果建筑物图片较小的话, 还会出现整栋
    建筑显示在画框外的情况. 因此还是选择contain更合适一些.
    """
    if method == "cover":
        if num_layers == 1:
            layer_offset = 0
        else:
            unit_offset = 1 / num_layers
            layer_offset = (layer_index-0.5) * unit_offset
           
        idx = int((building_index+layer_offset) / (buildings_per_layer-1) * (points_per_line - 1))
            
    return idx

def getForegroundUserDataID(user_data, building_index, buildings_per_layer):
    if not user_data:
        return None
    layer_data = user_data[0]

    if not layer_data:
        return None
    points_per_line = len(layer_data)

    idx = int((building_index + 0.5) / buildings_per_layer * (points_per_line-1))
    return idx