import numpy as np


def hybrid_nms(data, sorted_index, valid_count,
               max_output_size, iou_threshold, force_suppress,
               top_k, coord_start, id_index, score_index, zero, one):
    """Hybrid routing for non-maximum suppression.

    Parameters
    ----------
    data: tvm.Tensor or numpy NDArray
        Bounding boxes with class and score. 3-D tensor with shape
        [batch_size, num_anchors, 6].

    sorted_index : tvm.Tensor or numpy NDArray
        Bounding box indexes sorted by score, with shape
        [batch_size, num_anchors].

    valid_count : tvm.Tensor or numpy NDArray
        1-D tensor for valid number of boxes.

    max_output_size : tvm.const
        Max number of output valid boxes for each instance.
        By default all valid boxes are returned.

    iou_threshold : tvm.const
        Overlapping(IoU) threshold to suppress object with smaller score.

    force_suppress : tvm.const
        Whether to suppress all detections regardless of class_id.

    top_k : tvm.const
        Keep maximum top k detections before nms, -1 for no limit.

    coord_start : tvm.const
        Start index of the consecutive 4 coordinates.

    id_index : tvm.const
        index of the class categories, -1 to disable.

    score_index: tvm.const
        Index of the scores/confidence of boxes.

    zero: tvm.const
        Constant zero with the same dtype as data.

    one: tvm.const
        Constant one with the same dtype as data.

    Returns
    -------
    output : tvm.Tensor
        3-D tensor with shape [batch_size, num_anchors, 6].

    box_indices: tvm.Tensor
        2-D tensor with shape [batch_size, num_anchors].
    """
    batch_size = data.shape[0]
    num_anchors = data.shape[1]
    box_data_length = data.shape[2]
    #box_indices = output_tensor((batch_size, num_anchors), "int32")
    #output = output_tensor((batch_size,
    #                        num_anchors,
    #                        box_data_length,), data.dtype)

    for i in range(batch_size):
        if iou_threshold > 0:
            if valid_count[i] > 0:
                # Reorder output
                nkeep = valid_count[i]
                if 0 < top_k < nkeep:
                    nkeep = top_k
                for j in range(nkeep):
                    for k in range(box_data_length):
                        #output[i, j, k] = data[i, sorted_index[i, j], k]
                        output[i, j, k] = data[i, sorted_index[i, j], k]
                    box_indices[i, j] = sorted_index[i, j]
                if 0 < top_k < valid_count[i]:
                    for j in parallel(valid_count[i] - nkeep):
                        for k in range(box_data_length):
                            output[i, j + nkeep, k] = -one
                        box_indices[i, j + nkeep] = -1
            # Apply nms
            box_start_idx = coord_start
            batch_idx = i
            for j in range(valid_count[i]):
                if output[i, j, score_index] > 0 and (id_index < 0 or output[i, j, id_index] >= 0):
                    box_a_idx = j
                    for k in parallel(valid_count[i]):
                        check_iou = 0
                        if k > j and output[i, k, score_index] > 0 \
                                and (id_index < 0 or output[i, k, id_index] >= 0):
                            if force_suppress:
                                check_iou = 1
                            elif id_index < 0 or output[i, j, id_index] == output[i, k, id_index]:
                                check_iou = 1
                        if check_iou > 0:
                            a_l = output[batch_idx, box_a_idx, box_start_idx]
                            a_t = output[batch_idx, box_a_idx, box_start_idx + 1]
                            a_r = output[batch_idx, box_a_idx, box_start_idx + 2]
                            a_b = output[batch_idx, box_a_idx, box_start_idx + 3]
                            box_b_idx = k
                            b_t = output[batch_idx, box_b_idx, box_start_idx + 1]
                            b_b = output[batch_idx, box_b_idx, box_start_idx + 3]
                            b_l = output[batch_idx, box_b_idx, box_start_idx]
                            b_r = output[batch_idx, box_b_idx, box_start_idx + 2]
                            w = max(zero, min(a_r, b_r) - max(a_l, b_l))
                            h = max(zero, min(a_b, b_b) - max(a_t, b_t))
                            area = h * w
                            u = (a_r - a_l) * (a_b - a_t) + (b_r - b_l) * (b_b - b_t) - area
                            iou = zero if u <= zero else area / u
                            if iou >= iou_threshold:
                                output[i, k, score_index] = -one
                                if id_index >= 0:
                                    output[i, k, id_index] = -one
                                box_indices[i, k] = -1
        else:
            for j in parallel(valid_count[i]):
                for k in range(box_data_length):
                    output[i, j, k] = data[i, j, k]
                box_indices[i, j] = j
        # Set invalid entry to be -1
        for j in parallel(num_anchors - valid_count[i]):
            for k in range(box_data_length):
                output[i, j + valid_count[i], k] = -one
            box_indices[i, j + valid_count[i]] = -1
        # Only return max_output_size valid boxes
        num_valid_boxes = 0
        if max_output_size > 0:
            for j in range(valid_count[i]):
                if output[i, j, 0] >= zero:
                    if num_valid_boxes == max_output_size:
                        for k in range(box_data_length):
                            output[i, j, k] = -one
                        box_indices[i, j] = -1
                    else:
                        num_valid_boxes += 1
    return output, box_indices


#def hybrid_nms(data, sorted_index, valid_count,
#               max_output_size, iou_threshold, force_suppress,
#               top_k, coord_start, id_index, score_index, zero, one):


data = np.random.randn(1, 5, 6 )
print(data.shape)
sorted_index = [[1, 2, 3, 4, 5]]
valid_count = np.array([4])
hybrid_nms(data, sorted_index, valid_count, 0, 0.4, True, -1, 10, 10, 10, 0, 1) 
