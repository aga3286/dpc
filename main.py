import pandas as pd
from tkinter import *

from dpctool import create_dpc_dict, rank_hospital_by, select_hospital_from, preprocess_dpc, list_to_text, ranking_text


def prefecture_pushed(input):
    """
    prefecture_buttonを押した時に動くfunction
    prefectureに押した都道府県名を代入
    :param input:
    :return:
    """
    def inner():
        global prefecture
        prefecture = input
        # 疾患カテゴリーがすでに押されている場合には、新たに押した都道府県の病院ランキングを表示
        if target:
            text = ranking_text(prefecture, department, target, dpc_dict, hospitals_df)
            canvas.itemconfig(canvas_text, text=text)
    return inner


def department_pushed(input):
    """
    department_buttonを押したときに動くfunction
    その科のcategory_buttonを新規作成
    :param input:
    :return:
    """
    def inner():
        global category_buttons, department
        department = input
        dpc_df = dpc_dict[department][0]
        preprocessed_dpc_df, category_df = preprocess_dpc(dpc_df)
        selected_hospital_df = select_hospital_from(prefecture, hospitals_df, preprocessed_dpc_df)
        # またカテゴリーボタンは押されてないが、仮にindex0番目のカテゴリーを設定し、病院ランキングを表示するようにする
        target = category_df.index[0]
        ranking_list = rank_hospital_by(target, category_df, selected_hospital_df)['施設名'].head().tolist()
        canvas.itemconfig(canvas_text, text=f'{prefecture}\n{target}のランキング\n' + list_to_text(ranking_list))
        # もともとあったボタンは削除
        for category_button in category_buttons:
            category_button.destroy()
        # 新規にボタン作成　疾患カテゴリーを3列目
        for i, key in enumerate(category_df.index):
            category_button = Button(text=key, width=50, command=category_pushed(key))
            category_buttons.append(category_button)
            category_button.grid(row=i, column=3)
    return inner


def category_pushed(input):
    """
    category_buttonを押した時に動くfunction
    その県内疾患カテゴリーの病院ランキングを表示
    :param input:
    :return:
    """
    def inner():
        global target
        target = input
        text = ranking_text(prefecture, department, target, dpc_dict, hospitals_df)
        canvas.itemconfig(canvas_text, text=text)
    return inner


if __name__ == '__main__':
    dpc_dir_path = './data/dpc_data'
    hospitals_path = 'data/hospitals.xlsx'
    # dpcと病院のdf, 当道府県listを読み込み
    dpc_dict = create_dpc_dict(dpc_dir_path)
    hospitals_df = pd.read_excel(hospitals_path)
    prefectures = pd.read_csv('data/master/prefectures.csv')['都道府県'].tolist()
    prefecture = prefectures[15]  # prefectures.csvより作成

    # tkinterでGUI作成
    window = Tk()
    window.title('DPC')
    window.config(padx=20, pady=20)
    # rankingを表示するcanvasは4列目
    canvas = Canvas(width=500)
    canvas_text = canvas.create_text(250, 100, text='ここにランキングが入る')
    canvas.grid(row=0, column=4, rowspan=10)
    # 都道府県のボタンを0,1列目
    for i, key in enumerate(prefectures):
        prefecture_button = Button(text=key, width=5, command=prefecture_pushed(key))
        if i < 23:
            prefecture_button.grid(row=i, column=0)
        else:
            prefecture_button.grid(row=i - 23, column=1)
    # 疾患臓器のボタンを2列目
    for i, key in enumerate(dpc_dict):
        department_button = Button(text=key, width=40, command=department_pushed(key))
        department_button.grid(row=i, column=2)
    category_buttons = []
    target = False

    window.mainloop()
