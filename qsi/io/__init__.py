import os
import os.path
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from . import pre
from ..dr import lda

from ..vis import *
DATA_FOLDER = os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))) + "/data/"

DATASET_MAP = {'s4_formula': ('7341_C1.csv', ',', False, '7341_C1 desc.txt', ['Stage 4 (4-7 years) formula'],200),
               's3_formula': ('B3.csv', ',', False, 'B3 desc.txt', ['Stage 3 (12~36 months) infant formula'],200),
               's4_formula_c2': ('7341_C2.csv', ',', True, '7341_C2 desc.txt', ['Brand 1', 'Brand 2'], 1000),
               's4_formula_c3': ('7341.csv', ',', True, '7341 desc.txt', ['Brand 1', 'Brand 2', 'Brand 3'], 1000),
               'milk_tablet_candy': ('734b.csv', ',', False, '734b desc.txt', ['Compressed Milk Tablet Candy'], 200),
               'yogurt': ('7346.csv', ',', True, '7346 desc.txt', ["YL", "GM", "WQ", "MN"], 200),
               'vintage': ('7344.txt', '\t', False, '7344 desc.txt', ['8-year vintage'],200),
               'vintage_spi': ('7345.csv', ',', True, '7345 desc.txt', ["5Y", "8Y", "16Y", "26Y"],200),
               'vintage_526': ('7344_Y5Y26.csv', ',', True, '7344_Y5Y26 desc.txt', ["5Y", "26Y"], 2000),
               'beimu': ('754a_C2S_Beimu.txt', ',', True, '754a_C2S_Beimu desc.txt', ["Sichuan", "Zhejiang"], 300),
               'shihu_c2': ('754b_C2S_Shihu.csv', ',', True, '754b_C2S_Shihu desc.txt', ['Yunnan', 'Zhejiang'], 500),
               # 'shihu': ('754b.csv',',',True,'754b desc.txt',['Yunnan','Wenzhou','Panan1','Panan2']),
               'huangqi_rm': ('7044X_RAMAN.csv', ',', True, '7044X_RAMAN desc.txt', ['Inner Mongolia', 'Sichuan', 'Shanxi', 'Gansu'], 3000),
               'huangqi_uv': ('7143X_UV.csv', ',', True, '7143X_UV desc.txt', ['Inner Mongolia', 'Sichuan', 'Shanxi', 'Gansu'], 2),
               'huangqi_ims': ('704b_IMS.csv', ',', True, '704b_IMS desc.txt', ['Inner Mongolia', 'Sichuan', 'Shanxi', 'Gansu'], 5),
               'cheese': ('Cheese_RAMAN.csv', ',', True, 'Cheese_RAMAN desc.txt', ['MK', 'SL', 'YL'], 200),
               'huangjing': ('7a43.csv', ',', True, '7a43 desc.txt', ['Wild', 'Cultivated'], 3000),
               'huangjing2': ('7a47.csv', ',', True, '7a47 desc.txt', ['Red-Stem', 'Green-Stem'], 3000),
               'chaihu_rm': ('7a41.csv', ',', True, '7a41 desc.txt', ['Wild', 'Cultivated', 'B. smithii Wolff', 'Gansu', 'Shanxi', 'vinegar Concocted', 'Terrestrosin D'], 1500),
               'rice_cereal': ('7741_rice_cereal_rm.csv', ',', True, '7741_rice_cereal_rm desc.txt', ['LF', 'EB'], 3000),
               'organic_milk': ('MALDITOFMS_ORGANICMILK_7047_C02.csv', ',', True, 'MALDITOFMS_ORGANICMILK_7047_C02 desc.txt', ['inorganic', 'organic'], 1000),
               'milkpowder_enose': ('7747.pkl', ',', True, '7747 desc.txt', ['cn', 'au'], 200),
               # 'forsythia': ('7746.pkl',',',True,'7746 desc.txt', ["SX山西","HN河南","HB湖北","SHX陕西"]) # 该电子鼻数据未有效对齐
               'milkpowder_etongue': ('7744.pkl', ',', True, '7744 desc.txt', ['cn', 'au'], 200),
               # 该电子鼻数据未有效对齐
               'forsythia_etongue': ('7745.pkl', ',', True, '7745 desc.txt', ["SX山西", "HN河南", "HB湖北", "SHX陕西"], 200),
               'yimi_rm': ('yimi_raman.csv', ',', False, 'yimi_raman desc.txt', ['coix seed'], 200),
               'hangbaiju_rm': ('hangbaiju_raman.csv', ',', False, 'hangbaiju_raman desc.txt', ['chrysanthemum morifolium'], 200),
               'salt': ('7545.csv', ',', True, '7545 desc.txt', ["well salt", "sea salt"], 200),
               'chaihu_ms': ('7b43.csv', ',', True, '7b43 desc.txt', ["wild", "cultivated"], 200),
               'mouse_omics': ('metabolomics.txt', '\t', True, 'metabolomics desc.txt', ["control", "experiment"], 50000000)             
               }


def get_available_datasets():
    '''
    Returns available dataset names.    
    '''
    return list(DATASET_MAP.keys())


def id_to_path(id):
    '''
    Returns dataset metadata.
    '''
    return DATASET_MAP[id]


def load_dataset(id, SD=1, shift=None, x_range=None, y_subset=None, display=True):
    '''
    Load a built-in dataset.

    Parameters
    ----------
    x_range : e.g., list(range(0,500))
    y_subset : e.g., [0,3]

    Examples
    --------
    X, y, X_names, _, labels = io.load_dataset('milk_tablet_candy')
    '''

    path, delimiter, has_y, path_desc, labels, default_shift = id_to_path(id)
    print('load dataset from', path)

    if display:
        if shift is None:
            shift = default_shift
        X, y, X_names, labels = peek_dataset(
            DATA_FOLDER + path, delimiter, has_y, labels, SD, shift, x_range, y_subset)
    else:
        X, y, X_names, labels = open_dataset(
            DATA_FOLDER + path, delimiter, has_y, labels, x_range, y_subset)

    if os.path.exists(DATA_FOLDER + path_desc):
        f = open(DATA_FOLDER + path_desc, "r", encoding='UTF-8')
        desc = f.read()
        f.close()

        print(desc)

    else:
        desc = ''
    
    return X, y, X_names, desc, labels


def open_dataset(path, delimiter=',', has_y=True, labels = None, x_range=None, y_subset=None):
    '''
    Parameters
    ----------
    path : if the file extension is pkl, will use pickle.load(), otherwise use pandas.read_csv()
    has_y : boolean, whether there is y column, usually the 1st column.
    x_range : [250,2000] or None. If none, all features are kept.
    '''

    ext = os.path.splitext(path)[1]

    # special treatment for specific datasets
    if 'metabolomics.txt' in path:
        data = pd.read_csv(path, delimiter = '\t') # ,header=None
        X_names_mol = data.iloc[:5022,4].values.tolist() # molecules
        X = data.iloc[:5022,19:].T.values
        y = np.array([0]*int(len(X)/2) + [1]*int(len(X)/2) )
        X_names = list(map(float, data.iloc[:5022,1].values)) # m/z

        idx = np.argsort(X_names) # re-order by m/z
        X_names = np.array(X_names)[idx]
        X = X[:,idx]  # re-arrange columns to match X_names

    elif ext == '.pkl':

        with open(path, 'rb') as f:

            ds = pickle.load(f)
            X = ds['X']

            if has_y:
                y = ds['y']
            else:
                y = None

            if 'X_names' not in ds or ds['X_names'] is None:
                X_names = list(range(X.shape[1]))
            else:
                X_names = ds['X_names']

    else:

        # path = "github/data/754a_C2S_Beimu.txt"
        data = pd.read_csv(path, delimiter=delimiter)  # ,header=None
        # print('Total NAN: ', data.isnull().sum().sum(), '\n\n', data.isnull().sum().values)

        cols = data.shape[1]

        if has_y:

            # convert from pandas dataframe to numpy matrices
            X = data.iloc[:, 1:cols].values  # .values[:,::10]
            y = data.iloc[:, 0].values.ravel()  # first col is y label
            # use map(float, ) to convert the string list to float list
            # list(map(float, data.columns.values[1:])) # X_names = np.array(list(data)[1:])
            X_names = list(map(float, data.columns.values[1:]))

        else:

            X = data.values
            y = None

            # use map(float, ) to convert the string list to float list
            # X_names = np.array(list(data)[1:])
            X_names = list(map(float, data.columns.values))

    if x_range is not None:
        X = X[:, x_range]
        X_names = np.array(X_names)[x_range].tolist()

    if has_y and y_subset is not None:
        Xs = []
        ys = []

        for x, v in zip(X, y):
            if v in y_subset:
                Xs.append(x)
                # map to natrual label series, 0,1,2,..
                ys.append(y_subset.index(v))

        print('Use classes: ' + str(y_subset) +
              ', remapped to ' + str(list(range(len(y_subset)))))
        X = np.array(Xs)
        y = np.array(ys)

    if has_y and y is not None:
        print('X.shape', X.shape, ' y.shape', y.shape)
    else:
        print('X.shape', X.shape)

    cnt_nan = np.isnan(X).sum()
    if cnt_nan > 0:
        print('Found' + str(cnt_nan) +
              'NaN elements in X. You may need to purge NaN.')
    
    if labels is not None and labels != [] and y_subset is not None:
        labels = list(np.array(labels)[y_subset])

    return X, y, X_names, labels


def scatter_plot(X, y, labels=None, tags=None):
    '''
    Parameters
    ----------
    tags - You may pass "list(range(len(X_pca))" to tags to identify outliers.
    '''

    pca = PCA(n_components=2)  # keep the first 2 components
    X_pca = pca.fit_transform(X)
    plotComponents2D(X_pca, y, legends=labels, tags=tags)
    plt.title('PCA')
    plt.show()

    # for very-high dimensional data, lda/pls is very slow.
    if y is not None and X.shape[1] < 6000:

        X_lda = lda(X, y)
        # , tags = range(len(y)), ax = ax
        plotComponents2D(X_lda, y, legends=labels)
        plt.title('LDA`')
        plt.show()

        pls = PLSRegression(n_components=2, scale=False)
        X_pls = pls.fit(X, y).transform(X)
        # , tags = range(len(y)), ax = ax
        plotComponents2D(X_pls, y, legends=labels)
        # print('score = ', np.round(pls.score(X, y),3))
        plt.title('PLS')
        plt.show()


def draw_average(X, X_names, SD=1):

    matplotlib.rcParams.update({'font.size': 16})

    plt.figure(figsize=(20, 5))

    if SD > 0:
        plt.plot(X_names, X.mean(axis=0), "k", linewidth=1, label='averaged waveform $± ' +
                 str(SD) + '\sigma$ (' + str(len(X)) + ' samples)')
        plt.errorbar(X_names, X.mean(axis=0), X.std(axis=0)*SD,
                     color="dodgerblue", linewidth=3,
                     alpha=0.1)  # X.std(axis = 0)
    else:
        plt.plot(X_names, X.mean(axis=0), "k", linewidth=1,
                 label='averaged waveform' + ' (' + str(len(X)) + ' samples)')

    plt.legend()

    plt.title('Averaged Spectrum')
    # plt.xlabel(r'Wavenumber $(cm^{-1})$')
    # plt.ylabel('Raman signal')
    plt.yticks([])
    # plt.xticks([])
    plt.show()

    matplotlib.rcParams.update({'font.size': 12})


def draw_samples(X, y, X_names, titles=None, bdr=False):
    '''
    To draw the first K samples, call like this: draw_samples(X[:K], y[:K]...

    Parameters
    ----------    
    bdr : baseline drift removal using Butterworth high-pass filter
    '''

    matplotlib.rcParams.update({'font.size': 16})

    if titles is None:
        titles = []
        for idx, x in enumerate(X):
            title = 'Sample ' + str(idx)
            if y is not None:
                title = title + ', Class ' + str(y[idx])
            titles.append(title)

    if bdr:
        # Butterworth filter
        # axis = 0 for vertically; axis = 1 for horizontally
        X_bdr = pre.filter_dataset(X, nlc=0.002, nhc=None)
    else:
        X_bdr = X

    for x, xbdr, title in zip(X, X_bdr, titles):

        plt.figure(figsize=(20, 5))

        plt.plot(X_names, x, linewidth=1, label=title)
        if bdr:
            plt.plot(X_names, xbdr, linewidth=1,
                     label='baseline drift removal')

        plt.title(title)
        # plt.yticks([])
        plt.legend()
        plt.show()

    matplotlib.rcParams.update({'font.size': 12})


def draw_class_average(X, y, X_names, labels=None, SD=1, shift=200):
    '''
    Parameter
    ---------
    SD : Integer, show the +/- n-std errorbar. When SD = 0, will not show. 
    shift : y-direction shift to disperse waveforms of different classes.
    '''

    matplotlib.rcParams.update({'font.size': 18})

    plt.figure(figsize=(24, 10))

    if labels is None:
        labels = list(map(lambda s: 'Class ' + str(s), set(y)))

    for c, label in zip(set(y), labels):
        Xc = X[y == c]
        yc = y[y == c]

        if SD == 0:
            plt.plot(X_names, np.mean(Xc, axis=0) + c*shift,
                     label='Class ' + str(c) + ' (' + str(len(yc)) + ' samples)')

        else:  # show +/- std errorbar
            plt.errorbar(X_names, Xc.mean(axis=0) + shift*c, Xc.std(axis=0)*SD,
                         # color = ["blue","red","green","orange"][c],
                         linewidth=1,
                         alpha=0.2,
                         label=label + \
                         ' (' + str(len(yc)) + ' samples)' + \
                         ' mean ± ' + str(SD) + ' SD',
                         )  # X.std(axis = 0)
            plt.scatter(X_names, np.mean(Xc, axis=0).tolist() + c*shift,
                        # color = ["blue","red","green","orange"][c],
                        s=1
                        )

        plt.legend()

    plt.title(u'Averaged Spectrums for Each Category\n')
    # plt.xlabel(r'$ cm^{-1} $') # depending on it is Raman or MS
    plt.ylabel('Intensity')
    plt.yticks([])
    plt.show()

    matplotlib.rcParams.update({'font.size': 10})


def peek_dataset(path,  delimiter=',', has_y=True, labels=None, SD=1, shift=200, x_range=None, y_subset=None):

    X, y, X_names, labels = open_dataset(
        path, delimiter=delimiter, has_y=has_y, labels=labels, x_range=x_range, y_subset=y_subset)

    if len(X.shape) == 2:

        if y is None:
            draw_average(X, X_names)
        else:
            draw_class_average(X, y, X_names, labels, SD, shift)

        scatter_plot(X, y, labels=labels)

    elif len(X.shape) == 3:  # enose/etongue

        # Display one data sample in each category.

        if labels is None:
            labels = list(map(lambda s: 'Class ' + str(s), set(y)))

        matplotlib.rcParams.update({'font.size': 18})

        for c, label in zip(set(y), labels):
            Xc = X[y == c]
            yc = y[y == c]

            for sidx, x in enumerate(Xc):

                plt.figure(figsize=(30, 10))
                # print(np.mean(Xc,axis=0).ravel().tolist()[0])

                for idx, X_name in enumerate(X_names):  # X_names is channels
                    plt.plot(x[idx], label=X_name)

                plt.xlabel('time')
                # plt.ylabel('frequency difference') for enose or 'voltage' for etongue
                plt.legend(fontsize=20)

                plt.title(u'Sample ' + str(sidx) + ' in ' +
                          str(label))  # first sample
                plt.show()

                # break # only diplay 1st sample

        matplotlib.rcParams.update({'font.size': 10})

    return X, y, X_names, labels


def save_dataset(targe_path, X, y, X_names):
    '''
    Save X, y to a local csv/pkl file.
    When len(X.shape) > 2 (e.g., enose and etongue, must use pkl) 

    Parameters
    ----------
    X , y : must be numpy arrays
    X_names : the labels for each X feature
    '''

    if len(X.shape) == 2:  # can be saved as a tabular dataset

        dfX = pd.DataFrame(X)
        dfX.columns = X_names

        dfY = pd.DataFrame(y)
        dfY.columns = ['label']

        df = pd.concat([dfY, dfX], axis=1)
        df = df.sort_values(by=['label'], ascending=True)
        df.to_csv(targe_path, index=False)  # don't create the index column

    else:

        # create a dictionary
        ds = {
            "X": X,
            "y": y,
            "X_names": X_names
        }
        # save dictionary to pickle file
        with open(targe_path, "wb") as f:
            pickle.dump(ds, f)
