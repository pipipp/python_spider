# -*- coding:utf-8 -*-
def sort_statistics():
    s = "The Zen of Python, by Tim PetersBeautiful is better than ugly." \
        "Explicit is better than implicit.Simple is better than complex.Complex is better than complicated."
    total = s.split()
    data = []
    # 把标点符号去了
    for i in total:
        if '.' in i:
            split_line = i.split('.')
            for r in split_line:
                if r:
                    data.append(r)
                    break
        elif ',' in i:
            split_line = i.split(',')
            for r in split_line:
                if r:
                    data.append(r)
                    break
        else:
            data.append(i)
    # 计算所有单词出现的次数
    result = []
    for each in data:
        result.append([each, data.count(each)])
    print('所有单词出现次数统计结果：{}'.format(result))

    # 出现次数排序
    sort_result = []
    for each in result:
        if sort_result:
            index = 0
            for i in sort_result:
                if each[1] >= i[1]:
                    index = sort_result.index(i)
            sort_result.insert(index+1, each)
        else:
            sort_result.append(each)
    print('排名前五名的单词: {}'.format(sort_result[-5:]))


if __name__ == '__main__':
    sort_statistics()
