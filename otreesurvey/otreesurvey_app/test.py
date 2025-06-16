def smart_linebreak(text, threshold=15):
    if len(text) <= threshold:
        return text

    # Find middle point
    mid = len(text) // 2

    # Search for nearest space to the middle (first to the right, then to the left)
    right = text.find(' ', mid)
    left = text.rfind(' ', 0, mid)

    # Pick the best split point
    if right == -1 and left == -1:
        split_point = mid  # no spaces found, just split at middle
    elif right == -1:
        split_point = left
    elif left == -1:
        split_point = right
    else:
        # pick the closer one to mid
        split_point = left if (mid - left) <= (right - mid) else right

    # Insert line break
    return text[:split_point] + '\n' + text[split_point+1:]

test = "most of my friends rarely eat meat"
testx = smart_linebreak(test)
testx