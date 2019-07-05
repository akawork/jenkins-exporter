import re

if __name__ == "__main__":
    
    sname = 'item'
    dname = 'item_info'
    s = '_class,blocked,buildable,id,inQueueSince,stuck,task[name],why'

    res = re.findall(r'([_a-zA-Z0-9]+)',s)
    for r in res:
        x = re.sub(r'((?:[_]){0,1}[a-zA-Z0-9]+)','{}[\'\\1\'] = {}[\'\\1\']'.format(dname,sname),r)
        print(x)

