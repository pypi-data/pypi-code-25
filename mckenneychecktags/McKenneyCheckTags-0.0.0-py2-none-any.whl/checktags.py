def checktags(formtags):
    i = 0
    while i < len(formtags):
        formtags[i] = formtags[i].lstrip()
        formtags[i] = formtags[i].rstrip()
        i += 1

    i = 0
    x = 1
    duplicateTags = 0
    if len(formtags) > 1:
        while i < len(formtags) - 1:
            x = i + 1
            while x < len(formtags):
                if formtags[i] == formtags[x]:
                    duplicateTags = 1
                    x += 1
                else:
                    x += 1
            i += 1


    return duplicateTags