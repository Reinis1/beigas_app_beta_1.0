from bs4 import BeautifulSoup
import requests





def get_table(id='rs-class-table-11DIT'):
    url = "https://www.r64vsk.lv/5-12-klase/stundu-saraksts"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table', {'id': id})
    rows = table.find_all("tr")
    data = []

    for row in rows:
        cols = row.find_all('td')
        cols_data = []
        for col in cols:
            cols_data.append(col.text)
        data.append(cols_data)

    for i in range(3):
        data.pop(0)

    for index in range(len(data)-1):
        for day in range(5):
            if data[index][day].isnumeric() and not data[index+1][day].isnumeric():
                for item in range(len(data[index+1])):
                    if data[index+1][item] != "\n":
                        day_index = item
                        result = f"{data[index][day_index+1]} / {data[index+1][day_index]}"
                        data[index][day_index+1] = result

    data1 = []
    for inner_list in data:
        if inner_list[0].isnumeric():
            inner_list.pop(0)
            data1.append(inner_list)
    data = data1
    result = [[[]]]

    for y in range(0, 9, 2):
        daylist = []
        for index in range(len(data)):
            sublist = [data[index][y], data[index][y + 1]]
            daylist.append(sublist)
        result.append(daylist)

    result.pop(0)
    result = [[[x if x != '\n' else '' for x in sublist] for sublist in sublist2] for sublist2 in result]
    print(result)

    return result


def get_stundu_laiki():
    stundu_laiki = [
        [[8, 15], [8, 55]],     # 1
        [[9, 0], [9, 40]],      # 2
        [[9, 45], [10, 25]],    # 3
        [[10, 30], [11, 10]],   # 4
        [[11, 20], [12, 0]],    # 5
        [[12, 5], [12, 45]],    # 6
        [[12, 50], [13, 30]],   # 7
        [[13, 35], [14, 15]],
        [[14, 20], [15, 00]],  # 8
        [[15, 5], [17, 45]],    # 9
        [[16, 5], [17, 45]],    # 10
    ]
    return stundu_laiki

stundu_laiki = [
    [[8, 15], [8, 55]],     # 1
    [[9, 0], [9, 40]],      # 2
    [[9, 45], [10, 25]],    # 3
    [[10, 30], [11, 10]],   # 4
    [[11, 20], [12, 0]],    # 5
    [[12, 5], [12, 45]],    # 6
    [[12, 50], [13, 30]],   # 7
    [[13, 35], [14, 15]],   # 8
    [[14, 20], [15, 0]],    # 9
    [[15, 5], [15, 45]],    # 10
]



default_saraksts = [
    [["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],

     ],

    [["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],

     ],

    [["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],

     ],

    [["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],

     ],

    [["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],
     ["Nav ievadīts", "0"],

     ],
]
# default_saraksts[day]['][0]= 'matematika'

dictOfStrings = {'matemātika': 'Rumaka',
                         'latviešvaloda': 'Kalniņa',
                         'Literatūra': 'Kalniņa'}
