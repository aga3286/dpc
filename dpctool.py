import numpy as np
import pandas as pd
import glob
import os

def create_dpc_dict(dpc_dir_path):
    """
    dpc excel の入ったフォルダのパスからフォルダ内のデータを、{臓器名：dpcデータのdf, ...}のdictを返す
    :param dpc_dir_path:
    :return:
    """
    dpc_paths = glob.glob(os.path.join(dpc_dir_path, '*'))
    mdc_df = pd.read_csv('./data/master/mdc.csv')
    dpc_dict = {}
    for path in dpc_paths:
        dpc_df = pd.read_excel(path)
        columns = [col_name for col_name in dpc_df.columns if not 'Unnamed:' in col_name]
        mdc = int(columns[0][0:2])
        mdc_name = mdc_df[mdc_df['mdc'] == mdc]['name'].tolist()[0]
        dpc_dict.setdefault(mdc_name, []).append(dpc_df)
    return dpc_dict


def rank_hospital_by(target, category_df, dpc_df):
    """
    疾患カテゴリーにおける患者数で病院をランクづけしたdfを返す
    :param target:
    :param category_df:
    :param dpc_df:
    :return:
    """
    dpc_df = dpc_df.copy().replace('-', np.nan)
    start_idx = category_df.loc[target]['start_idx']
    end_idx = category_df.loc[target]['end_idx']
    interval = category_df.iloc[0]['end_idx'] - category_df.iloc[0]['start_idx']
    if end_idx == 0:
        total_cases = dpc_df.iloc[:, start_idx:start_idx + interval].sum(axis=1)
    else:
        total_cases = dpc_df.iloc[:, start_idx:end_idx].sum(axis=1)
    total_df = dpc_df.iloc[:][['告示番号', '施設名']]
    total_df['total'] = total_cases
    return total_df.sort_values('total', ascending=False)


def select_hospital_from(prefecture, hospitals_df, dpc_df):
    """
    目的の県のdpcデータの病院のdpc_dfを返す
    :param prefecture:
    :param hospitals_df:
    :param dpc_df:
    :return:
    """
    hospital_num = hospitals_df[hospitals_df['都道\n府県'] == prefecture]['告示番号\n※1'].tolist()
    hospital_id = []
    for idx, num in enumerate(dpc_df['告示番号']):
        if num in hospital_num:
            hospital_id.append(idx)
    return dpc_df.iloc[hospital_id]


def preprocess_dpc(dpc_df):
    """
    DPCデータから加工したDPCと疾患カテゴリーのdfを返す
    :param dpc_df:
    :return:
    """
    # 科内の疾患カテゴリーとそのカテゴリーが始まるcolumnのインデックスをdictにする
    category_idx = {}
    for idx, category in enumerate(dpc_df.iloc[0]):
        category_idx[category] = idx

    # 科内の疾患カテゴリーとそのカテゴリーが始まるcolumnと終わりのcolumnをdataframeにする
    category_list = []
    for k in category_idx:
        category_list.append([k, category_idx[k]])
    category_df = pd.DataFrame(category_list, columns=['category', 'start_idx'])
    category_df.dropna(inplace=True)
    end_idx = category_df['start_idx'][1:].tolist()
    end_idx.append(0)
    category_df['end_idx'] = end_idx
    category_df.set_index('category', inplace=True)
    category_df['end_idx'] = (
            category_df['start_idx'] + (category_df['end_idx'] - category_df['start_idx']) / 2).astype(int)
    category_df['end_idx'][-1] = 0

    # dpcもとデータの上３行を除く
    dpc_df.columns = dpc_df.iloc[2]
    dpc_df = dpc_df.iloc[3:]

    return dpc_df, category_df

def list_to_text(ranking_list):
    """
    リスト内のelementを昇順にランクづけしたtextにする
    :param ranking_list:
    :return:
    """
    text = [f'{idx + 1}. {hospital}' for idx, hospital in enumerate(ranking_list)]
    text = '\n'.join(text)
    return text

def ranking_text(prefecture, department, target, dpc_dict, hospitals_df):
    """
    県、疾患臓器（科）、臓器内の疾患カテゴリーを指定し、ランキングを作成、textにする
    :param prefecture:
    :param department:
    :param target:
    :return:
    """


    dpc_df = dpc_dict[department][0]
    preprocessed_dpc_df, category_df = preprocess_dpc(dpc_df)
    selected_hospital_df = select_hospital_from(prefecture, hospitals_df, preprocessed_dpc_df)
    ranking_list = rank_hospital_by(target, category_df, selected_hospital_df)['施設名'].head().tolist()
    text = f'{prefecture}\n{target}のランキング\n' + list_to_text(ranking_list)
    return text
